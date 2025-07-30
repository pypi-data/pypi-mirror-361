import warnings

import numpy as np
from scipy.interpolate import splev, splprep
from tqdm.auto import tqdm

from biolocsim.core.collision import VoxelGrid
from biolocsim.utils.geometry import get_perpendicular_vectors


class MicrotubuleGenerator:
    def __init__(self, config):
        self.config = config
        self.dims = np.array(config["volume_dims"])  # units: nm
        self.padding = np.array(config.get("padding", 0))
        self.resolution = config["resolution"]  # In nm/voxel, can be isotropic (float) or anisotropic (list)
        self.rng = np.random.default_rng(config.get("seed"))
        self.verbose = config.get("verbose", False)
        self.generation_mode = config.get("generation_mode", "random")
        self.fixed_corner_faces = None

        if self.dims.shape != (3,):
            if isinstance(self.dims, (int, float)):
                self.dims = np.array([self.dims, self.dims, self.dims])
            else:
                raise ValueError("volume_dims must have 3 components (x, y, z).")
        if self.padding.shape != (3,):
            if isinstance(self.padding, (int, float)):
                self.padding = np.array([self.padding, self.padding, self.padding])
            else:
                raise ValueError("Padding must be a single number or a list/array of 3 numbers.")

    def _validate_control_points(self, points, min_angle_deg, min_distance_nm):
        """
        Validates the geometry of control points.
        Checks for minimum angle between segments and minimum distance between points.
        """
        # Check distance between consecutive points
        if min_distance_nm > 0:
            distances = np.linalg.norm(np.diff(points, axis=0), axis=1)
            if np.any(distances < min_distance_nm):
                return False  # Points are too close

        # Check angle for every three consecutive points
        if min_angle_deg > 0 and len(points) > 2:
            for i in range(1, len(points) - 1):
                v_prev = points[i - 1] - points[i]
                v_next = points[i + 1] - points[i]

                norm_prev = np.linalg.norm(v_prev)
                norm_next = np.linalg.norm(v_next)

                if norm_prev == 0 or norm_next == 0:
                    return False  # Collinear/identical points are invalid

                cosine_angle = np.dot(v_prev, v_next) / (norm_prev * norm_next)
                angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
                angle_deg = np.degrees(angle)

                if angle_deg < min_angle_deg:
                    return False  # Angle is too sharp

        return True

    def _sort_points_nearest_neighbor(self, points):
        """Sorts points using a nearest-neighbor greedy algorithm to form a path."""
        if len(points) <= 1:
            return points

        path = [0]
        remaining_indices = list(range(1, len(points)))

        while remaining_indices:
            last_point_idx = path[-1]
            last_point = points[last_point_idx]

            # Find distances to all remaining points
            distances = np.linalg.norm(points[remaining_indices] - last_point, axis=1)

            # Find the index of the nearest point (relative to remaining_indices)
            nearest_in_remaining_idx = np.argmin(distances)

            # Get the original index and move it from remaining to path
            original_idx = remaining_indices.pop(nearest_in_remaining_idx)
            path.append(original_idx)

        return points[path]

    def _splprep_with_warning_check(self, points_T, s, k):
        """Wraps splprep to catch specific RuntimeWarnings about convergence."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always", RuntimeWarning)
            tck, u = splprep(points_T, s=s, k=k)
            warning_raised = any("The maximal number of iterations" in str(warn.message) for warn in w)
        return tck, u, warning_raised

    def _generate_point_on_boundary(self, allowed_faces=None):
        """
        Generates a single random point on one of the 4 XY faces of the volume.
        An optional list of allowed_faces (0-3) can be provided.
        Faces are: 0 (x=0), 1 (x=max), 2 (y=0), 3 (y=max).
        """
        if allowed_faces is None:
            face = self.rng.integers(4)
        else:
            face = self.rng.choice(allowed_faces)

        point = np.zeros(3)

        if face == 0:  # x=0
            point[0] = 0
            point[1] = self.rng.random() * self.dims[1]
            point[2] = self.rng.random() * self.dims[2]
        elif face == 1:  # x=max
            point[0] = self.dims[0]
            point[1] = self.rng.random() * self.dims[1]
            point[2] = self.rng.random() * self.dims[2]
        elif face == 2:  # y=0
            point[0] = self.rng.random() * self.dims[0]
            point[1] = 0
            point[2] = self.rng.random() * self.dims[2]
        else:  # y=max, face == 3
            point[0] = self.rng.random() * self.dims[0]
            point[1] = self.dims[1]
            point[2] = self.rng.random() * self.dims[2]
        return point, face

    def _generate_free_point(self, collision_grid, on_boundary=False, max_attempts=50, allowed_faces=None):
        """Generates a single random point, ensuring it's not in a collision zone."""
        radius = self.config.get("collision_radius", self.config["tube_radius"])
        for _ in range(max_attempts):
            face = -1  # Default value for face if not on boundary
            if on_boundary:
                point, face = self._generate_point_on_boundary(allowed_faces=allowed_faces)
            else:
                point = self.rng.random(3) * self.dims

            # Check for collision at this single point
            if not collision_grid.check_collision(np.array([point]), radius):
                return point, face
        return None, -1  # Failed to find a free point

    def _generate_single_tube_centerline(self, collision_grid):
        """
        Generate a B-spline centerline, retrying until control points are valid.
        Control points are preferably generated in empty space.
        """
        max_attempts = self.config.get("max_attempts_per_tube", 100)
        min_angle = self.config.get("min_control_point_angle", 0)
        min_dist = self.config.get("min_control_point_distance", 0)
        warning_raised = False

        for _ in range(max_attempts):
            # 1. Generate a candidate set of control points
            num_control_points = self.rng.integers(
                self.config["control_points_range"][0],
                self.config["control_points_range"][1] + 1,
            )

            control_points_list = []
            generate_on_boundary = self.config.get("generate_on_boundary", True)

            if num_control_points < 2:
                # For 0 or 1 control points, boundary logic is not applicable.
                point, _ = self._generate_free_point(collision_grid, on_boundary=False)
                if point is not None:
                    control_points_list.append(point)
                # If even one point can't be generated, this attempt will fail.
            else:  # num_control_points >= 2
                allowed_faces_for_start = None
                if generate_on_boundary and self.generation_mode == "corner":
                    if self.fixed_corner_faces is None:
                        # First tube in "corner" mode: establish the corner for this run.
                        # A corner is defined by one x-face (0 or 1) and one y-face (2 or 3).
                        x_face = self.rng.choice([0, 1])
                        y_face = self.rng.choice([2, 3])
                        self.fixed_corner_faces = [x_face, y_face]
                    # For any tube in this run, pick one of the two fixed faces for the start point.
                    allowed_faces_for_start = [self.rng.choice(self.fixed_corner_faces)]

                start_point, start_face = self._generate_free_point(
                    collision_grid,
                    on_boundary=generate_on_boundary,
                    allowed_faces=allowed_faces_for_start,
                )
                if start_point is None:
                    continue  # Failed to find a free start point

                allowed_faces_for_end = None
                if generate_on_boundary and start_face != -1:
                    if self.generation_mode == "corner":
                        # End point must be on the other face of the established corner.
                        if start_face == self.fixed_corner_faces[0]:
                            allowed_faces_for_end = [self.fixed_corner_faces[1]]
                        else:
                            allowed_faces_for_end = [self.fixed_corner_faces[0]]
                    elif self.generation_mode == "center":
                        # Opposite faces. If start_face is 0, end must be 1.
                        if start_face == 0:
                            allowed_faces_for_end = [1]
                        elif start_face == 1:
                            allowed_faces_for_end = [0]
                        elif start_face == 2:
                            allowed_faces_for_end = [3]
                        elif start_face == 3:
                            allowed_faces_for_end = [2]
                    # For "random" mode, allowed_faces_for_end remains None (all faces allowed)

                end_point, _ = self._generate_free_point(
                    collision_grid,
                    on_boundary=generate_on_boundary,
                    allowed_faces=allowed_faces_for_end,
                )
                if end_point is None:
                    continue  # Failed to find a free end point

                internal_points = []
                num_internal_points = num_control_points - 2
                if num_internal_points > 0:
                    for _ in range(num_internal_points):
                        # Internal points are never on the boundary.
                        ip, _ = self._generate_free_point(collision_grid, on_boundary=False)
                        if ip is not None:
                            internal_points.append(ip)

                    if len(internal_points) != num_internal_points:
                        continue  # Failed to generate all internal points

                    internal_points = np.array(internal_points)
                    path_vector = end_point - start_point
                    if np.linalg.norm(path_vector) > 1e-6:
                        projections = np.dot(internal_points - start_point, path_vector)
                        sorted_indices = np.argsort(projections)
                        sorted_internal_points = internal_points[sorted_indices]
                        control_points = np.vstack([start_point, sorted_internal_points, end_point])
                    else:
                        control_points_to_sort = np.vstack([start_point, internal_points])
                        sorted_path = self._sort_points_nearest_neighbor(control_points_to_sort)
                        control_points = np.vstack([sorted_path, end_point])
                else:  # No internal points
                    control_points = np.array([start_point, end_point])

            if "control_points" not in locals() and not control_points_list:
                continue

            if not control_points_list:
                control_points = np.array(control_points)
            else:
                control_points = np.array(control_points_list)

            # 2. Validate the geometry of the control points
            if self._validate_control_points(control_points, min_angle, min_dist):
                # Found a valid set of points, proceed to create spline
                tck, u, warning_raised = self._splprep_with_warning_check(
                    control_points.T,
                    s=self.config.get("smoothness", 0),
                    k=self.config.get("spline_degree", 2),
                )
                spacing = self.config.get("centerline_point_spacing", 1.0)
                centerline_points = self._sample_spline_uniformly(tck, spacing)
                return centerline_points, tck, control_points, warning_raised

        # If loop finishes, all attempts to generate valid points failed
        return None, None, None, False

    def _sample_spline_uniformly(self, tck, spacing):
        """
        Samples a B-spline uniformly by arc length.
        """
        # Use a high number of points for initial sampling to approximate the curve length
        u_oversample = np.linspace(0, 1, self.config.get("centerline_sampling_points", 10000))
        points = np.array(splev(u_oversample, tck)).T

        # Calculate cumulative arc length
        distances = np.sqrt(np.sum(np.diff(points, axis=0) ** 2, axis=1))
        arc_length = np.insert(np.cumsum(distances), 0, 0)
        total_length = arc_length[-1]

        # Determine number of points based on desired spacing
        num_samples = int(np.ceil(total_length / spacing))
        if num_samples < 2:
            num_samples = 2

        # Create new sample points at uniform distances
        u_uniform = np.interp(np.linspace(0, total_length, num_samples), arc_length, u_oversample)

        # Evaluate spline at new u values
        centerline_points = np.array(splev(u_uniform, tck)).T
        return centerline_points

    def _adjust_control_points(self, control_points, centerline, colliding_indices, collision_grid, radius, step_size):
        """
        Adjusts control points to steer the curve away from collisions using a
        physically-inspired influence model.
        """
        new_control_points = control_points.copy()

        # Accumulate adjustment vectors for each control point
        cp_adjustments = np.zeros_like(new_control_points, dtype=float)

        for i in colliding_indices:
            colliding_point = centerline[i]
            repulsion_vector = collision_grid.get_repulsion_vector(colliding_point, radius)

            if np.linalg.norm(repulsion_vector) == 0:
                continue

            # Calculate influence based on inverse square distance to all control points
            distances_sq = np.sum((control_points - colliding_point) ** 2, axis=1)
            influences = 1.0 / (distances_sq + 1e-9)  # Add epsilon to avoid division by zero

            # Distribute the repulsion force to all control points based on influence
            # The total force applied should be proportional to the repulsion vector
            total_influence = np.sum(influences)
            distributed_repulsion = repulsion_vector * (influences / total_influence)[:, np.newaxis]
            cp_adjustments += distributed_repulsion

        # Normalize and apply the final adjustments
        if np.linalg.norm(cp_adjustments) > 1e-9:
            # Scale the adjustments so the largest movement corresponds to the given step_size
            max_movement = np.max(np.linalg.norm(cp_adjustments, axis=1))
            if max_movement > 1e-9:
                scaling_factor = step_size / max_movement
                new_control_points = new_control_points + cp_adjustments * scaling_factor

        return new_control_points

    def _generate_surface_points(self, centerline_points, tube_radius):
        """Generate points on the surface of a microtubule from its centerline."""
        if len(centerline_points) < 2:
            return np.array([]), False

        surface_points = []

        # 1. Calculate the total arc length of the centerline
        distances = np.linalg.norm(np.diff(centerline_points, axis=0), axis=1)
        arc_lengths = np.insert(np.cumsum(distances), 0, 0)
        total_length = arc_lengths[-1]

        if total_length < 1e-6:
            return np.array([]), False

        # 2. Determine total number of points from a linear density
        centerline_spacing = self.config.get("centerline_point_spacing", 1.0)
        linear_density = self.config["surface_points_per_sample"] / centerline_spacing
        num_surface_points = int(total_length * linear_density)

        if num_surface_points == 0:
            return np.array([]), False

        # 3. Get tangents by fitting a new spline to the uniformly sampled centerline.
        # This is a robust way to get smooth tangents.
        tck, u, warning_raised = self._splprep_with_warning_check(
            centerline_points.T, s=0, k=self.config.get("spline_degree", 2)
        )
        # We need u-values that correspond to arc-length for interpolation
        u_uniform = np.interp(arc_lengths, arc_lengths, u)

        # --- Random sampling method ---
        # Generate all random values at once for efficiency
        rand_distances = self.rng.random(num_surface_points) * total_length
        rand_angles = self.rng.random(num_surface_points) * 2 * np.pi

        for i in range(num_surface_points):
            dist_along_curve = rand_distances[i]
            theta = rand_angles[i]

            # Interpolate to find centerline point and tangent at this distance
            u_interp = np.interp(dist_along_curve, arc_lengths, u_uniform)
            point = np.array(splev(u_interp, tck, der=0)).T
            tangent = np.array(splev(u_interp, tck, der=1)).T

            norm_tangent = np.linalg.norm(tangent)
            if norm_tangent < 1e-6:
                continue  # Skip point if tangent is degenerate
            tangent /= norm_tangent

            # Get perpendicular vectors for the local coordinate system
            v_perp1, v_perp2 = get_perpendicular_vectors(tangent)

            # Calculate the final surface point position
            p = point + tube_radius * (np.cos(theta) * v_perp1 + np.sin(theta) * v_perp2)

            # --- Add surface jitter along the tangent ---
            if self.config.get("add_surface_jitter", False):
                jitter_std = self.config.get("surface_jitter_along_tangent_std", 0.0)
                if jitter_std > 0:
                    jitter = self.rng.normal(0, jitter_std)
                    p += jitter * tangent

            surface_points.append(p)

        surface_points = np.array(surface_points)
        min_bounds = -self.padding
        max_bounds = self.dims + self.padding

        # Final check to ensure all points are within the padded volume
        in_bounds_x = (surface_points[:, 0] >= min_bounds[0]) & (surface_points[:, 0] < max_bounds[0])
        in_bounds_y = (surface_points[:, 1] >= min_bounds[1]) & (surface_points[:, 1] < max_bounds[1])
        in_bounds_z = (surface_points[:, 2] >= min_bounds[2]) & (surface_points[:, 2] < max_bounds[2])
        in_bounds = in_bounds_x & in_bounds_y & in_bounds_z

        return surface_points[in_bounds], warning_raised

    def generate(self):
        """
        Generate a complete microtubule point cloud simulation.
        """
        self.fixed_corner_faces = None  # Reset for each new generation run
        num_tubes = self.config["num_tubes"]
        tube_radius = self.config["tube_radius"]
        collision_radius = self.config.get("collision_radius", tube_radius)
        max_attempts_per_tube = self.config.get("max_attempts_per_tube", 100)
        max_adjustment_attempts = self.config.get("max_adjustment_attempts", 5)
        initial_adjustment_step = self.config.get("adjustment_step", 50)
        num_adjustment_sub_steps = 3  # Number of times to try smaller steps

        collision_grid = VoxelGrid(self.dims, self.resolution)

        all_tubes_points_with_ids = []
        all_centerlines = []
        generated_tubes = 0
        warnings_in_successful_tubes = 0

        # Get validation parameters once
        min_angle = self.config.get("min_control_point_angle", 0)
        min_dist = self.config.get("min_control_point_distance", 0)

        pbar = tqdm(
            range(num_tubes),
            desc="Generating Microtubules",
            disable=not self.verbose,
        )
        for i in pbar:
            tube_has_warning = False
            for attempt in range(max_attempts_per_tube):
                (
                    centerline,
                    tck,
                    control_points,
                    warning_raised,
                ) = self._generate_single_tube_centerline(collision_grid)
                if centerline is None:
                    continue  # Control point generation failed validation, try again.

                if warning_raised:
                    tube_has_warning = True

                is_resolved = False

                for _ in range(max_adjustment_attempts):
                    colliding_indices = collision_grid.check_collision(centerline, collision_radius)
                    if not colliding_indices:
                        is_resolved = True
                        break

                    # Adaptive adjustment strategy
                    found_valid_adjustment = False
                    current_adjustment_step = initial_adjustment_step

                    for _ in range(num_adjustment_sub_steps):
                        new_control_points = self._adjust_control_points(
                            control_points,
                            centerline,
                            colliding_indices,
                            collision_grid,
                            collision_radius,
                            step_size=current_adjustment_step,
                        )

                        # Validate the adjusted control points before proceeding
                        if self._validate_control_points(new_control_points, min_angle, min_dist):
                            control_points = new_control_points
                            found_valid_adjustment = True
                            break  # Found a valid adjustment, proceed
                        else:
                            # Adjustment was too aggressive, reduce step size and retry
                            current_adjustment_step /= 2.0

                    if not found_valid_adjustment:
                        # All sub-steps failed to produce a valid geometry.
                        # Break adjustment loop and try a new tube from scratch.
                        break

                    tck, u, warning_raised = self._splprep_with_warning_check(
                        control_points.T,
                        s=self.config.get("smoothness", 0),
                        k=self.config.get("spline_degree", 2),
                    )
                    if warning_raised:
                        tube_has_warning = True

                    spacing = self.config.get("centerline_point_spacing", 1.0)
                    centerline = self._sample_spline_uniformly(tck, spacing)

                if is_resolved:
                    # Final check on centerline before generating surface is REMOVED
                    # The final point cloud will be clipped anyway in _generate_surface_points.
                    # in_bounds_x = (centerline[:, 0] >= 0) & (centerline[:, 0] < self.dims[0])
                    # in_bounds_y = (centerline[:, 1] >= 0) & (centerline[:, 1] < self.dims[1])
                    # in_bounds_z = (centerline[:, 2] >= 0) & (centerline[:, 2] < self.dims[2])

                    # if not np.all(in_bounds_x & in_bounds_y & in_bounds_z):
                    #     # This tube is invalid, try a new one
                    #     continue

                    collision_grid.add_curve(centerline, collision_radius)
                    (
                        surface_points,
                        warning_raised,
                    ) = self._generate_surface_points(centerline, tube_radius)

                    if warning_raised:
                        tube_has_warning = True

                    if surface_points.size > 0:
                        all_centerlines.append(centerline)
                        generated_tubes += 1

                        # Add instance ID column
                        instance_ids = np.full((surface_points.shape[0], 1), generated_tubes)
                        points_with_id = np.hstack([surface_points, instance_ids])
                        all_tubes_points_with_ids.append(points_with_id)

                        if tube_has_warning:
                            warnings_in_successful_tubes += 1

                        pbar.set_postfix(
                            {
                                "successful": f"{generated_tubes}/{num_tubes}",
                                "warnings": f"{warnings_in_successful_tubes}",
                            }
                        )

                        break
            else:
                if self.verbose:
                    # This message is still useful to show failures.
                    tqdm.write(f"Failed to generate tube {i + 1} after {max_attempts_per_tube} attempts.")

        if self.verbose:
            pbar.close()

        if not all_tubes_points_with_ids:
            points = np.empty((0, 4))
        else:
            points = np.concatenate(all_tubes_points_with_ids, axis=0)

        # --- Apply localization noise ---
        if self.config.get("add_localization_noise", False) and points.size > 0:
            loc_precision = self.config.get("localization_precision", 0.0)
            if np.any(np.array(loc_precision) > 0):
                noise = self.rng.normal(loc=0.0, scale=loc_precision, size=(points.shape[0], 3))
                points[:, :3] += noise

        # --- Add background noise ---
        if self.config.get("add_background_noise", False):
            bg_density = self.config.get("background_noise_density", 0.0)
            if bg_density > 0:
                min_bounds_bg = -self.padding
                max_bounds_bg = self.dims + self.padding
                volume_dims = max_bounds_bg - min_bounds_bg
                volume = np.prod(volume_dims)
                num_bg_points = int(volume * bg_density)

                if num_bg_points > 0:
                    bg_points = self.rng.uniform(low=min_bounds_bg, high=max_bounds_bg, size=(num_bg_points, 3))
                    # Background points have ID 0
                    bg_ids = np.zeros((num_bg_points, 1))
                    bg_points_with_ids = np.hstack([bg_points, bg_ids])

                    if points.size > 0:
                        points = np.vstack([points, bg_points_with_ids])
                    else:
                        points = bg_points_with_ids

        # --- Final clipping to ensure all points are within the padded volume ---
        if points.size > 0:
            min_bounds = -self.padding
            max_bounds = self.dims + self.padding
            in_bounds_x = (points[:, 0] >= min_bounds[0]) & (points[:, 0] < max_bounds[0])
            in_bounds_y = (points[:, 1] >= min_bounds[1]) & (points[:, 1] < max_bounds[1])
            in_bounds_z = (points[:, 2] >= min_bounds[2]) & (points[:, 2] < max_bounds[2])
            points = points[in_bounds_x & in_bounds_y & in_bounds_z]

        success_rate = generated_tubes / num_tubes if num_tubes > 0 else 0.0
        warning_rate_on_success = warnings_in_successful_tubes / generated_tubes if generated_tubes > 0 else 0.0

        stats = {
            "generated_tubes": generated_tubes,
            "requested_tubes": num_tubes,
            "success_rate": success_rate,
            "warnings_in_successful_tubes": warnings_in_successful_tubes,
            "warning_rate_on_success": warning_rate_on_success,
            "total_points": points.shape[0] if points.size > 0 else 0,
        }

        return points, stats, all_centerlines
