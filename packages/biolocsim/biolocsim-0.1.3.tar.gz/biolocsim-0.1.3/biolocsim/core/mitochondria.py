import numpy as np
from scipy.ndimage import binary_erosion
from tqdm.auto import tqdm


class MitochondriaGenerator:
    """
    Generates 3D point clouds of mitochondria using a persistent random walk model.

    This generator builds mitochondria segment by segment in a 3D voxel grid,
    handling collisions by "carving" out overlapping regions.
    """

    def __init__(self, config):
        self.config = config
        self.rng = np.random.default_rng(config.get("seed"))
        self.verbose = config.get("verbose", False)

        self.allow_boundary_clipping = config.get("allow_boundary_clipping", True)
        self.max_generation_attempts = config.get("max_generation_attempts", 10)

        # Physical dimensions in nm
        self.dims = np.array(config["volume_dims"])
        self.resolution = config["resolution"]

        # Grid dimensions in voxels (Z, Y, X order for numpy)
        self.grid_dims = tuple(np.ceil(self.dims / self.resolution).astype(int)[::-1])

        # Branching parameters
        self.enable_branching = config.get("enable_branching", False)
        self.branch_prob_per_step = config.get("branch_prob_per_step", 0.01)
        self.branch_angle_deg_mean = config.get("branch_angle_deg_mean", 45)
        self.branch_angle_deg_std = config.get("branch_angle_deg_std", 10)

        # Parameters for radius dynamics
        # Higher value = smoother radius change along the length.
        self.radius_autocorrelation_r1 = config.get("radius_autocorrelation_r1", 60.0)
        self.radius_autocorrelation_r2 = config.get("radius_autocorrelation_r2", 30.0)

        # Parameter to bias random walk towards the XY plane
        # A value of 1.0 is isotropic (no bias). Values < 1.0 dampen vertical movement.
        self.z_axis_dampening = config.get("z_axis_dampening", 1.0)

        # The main volume grid, storing occupied voxels (like mito_viewable)
        self.volume_grid = np.zeros(self.grid_dims, dtype=np.bool_)

        # A map to store the ID of the mitochondrion at each voxel
        self.label_map = np.zeros(self.grid_dims, dtype=np.uint16)

        # Padding for background noise generation, if any
        self.padding = np.array(config.get("padding", [0, 0, 0]))

    def _create_ellipsoid_mask(self, center_vx, radius1_vx, radius2_vx):
        """
        Creates a boolean mask for an ellipsoid within the main grid.
        Equivalent to crop_sphere.m.
        """
        # Calculate bounding box in voxel coordinates
        max_radius = np.ceil(max(radius1_vx, radius2_vx)).astype(int)
        min_coords = np.maximum(0, center_vx - max_radius)
        max_coords = np.minimum(self.grid_dims, center_vx + max_radius + 1)

        # Create a grid of coordinates for the bounding box
        z, y, x = np.ogrid[min_coords[0] : max_coords[0], min_coords[1] : max_coords[1], min_coords[2] : max_coords[2]]

        # Denominator should not be zero
        r1_safe = max(radius1_vx, 1e-6)
        r2_safe = max(radius2_vx, 1e-6)

        # Calculate squared distances from the center
        dist_sq = (
            ((z - center_vx[0]) / r2_safe) ** 2
            + ((y - center_vx[1]) / r1_safe) ** 2
            + ((x - center_vx[2]) / r1_safe) ** 2
        )

        mask = dist_sq <= 1

        # Slices to place the mask in the main grid
        slices = (
            slice(min_coords[0], max_coords[0]),
            slice(min_coords[1], max_coords[1]),
            slice(min_coords[2], max_coords[2]),
        )

        return mask, slices

    def _generate_single_mito_network(self):
        """
        Generates a single mitochondrion centerline network, potentially with branches.
        This closely follows the logic in sim_mito_3D_2.m and adds branching.
        """
        length_nm = self.rng.uniform(
            self.config["length_mean"] * (1 - self.config["length_heterogeneity"]),
            self.config["length_mean"] * (1 + self.config["length_heterogeneity"]),
        )
        if length_nm <= 0:
            return None, None, None

        persistence_length_vx = self.config["persistence_length"] / self.resolution
        step_size_vx = self.config["step_size"] / self.resolution
        num_steps = int(length_nm / self.config["step_size"])

        if num_steps < 2:
            return None, None, None

        margin = 0.125
        min_coords_nm = self.dims * margin
        max_coords_nm = self.dims * (1 - margin)

        # --- Start position selection ---
        # To avoid crowding, we can search for a start position in a sparse area.
        # "start_pos_search_candidates": Number of random points to test (e.g., 20).
        # "start_pos_search_radius_nm": Radius in nm to check for existing mitochondria (e.g., 1000).
        num_candidates = self.config.get("start_pos_search_candidates", 1)

        if num_candidates > 1 and np.any(self.volume_grid):
            search_radius_nm = self.config.get("start_pos_search_radius_nm", self.config["radius_mean"] * 2)
            search_radius_vx = int(search_radius_nm / self.resolution)

            best_pos = None
            min_density = float("inf")

            for _ in range(num_candidates):
                # Generate a random center position in nm (x,y,z), then convert to voxels (z,y,x)
                candidate_center_xyz_nm = self.rng.uniform(min_coords_nm, max_coords_nm)
                candidate_center_vx = (candidate_center_xyz_nm / self.resolution)[::-1].astype(int)

                # Define bounding box for density check
                min_v = np.maximum(0, candidate_center_vx - search_radius_vx)
                max_v = np.minimum(self.grid_dims, candidate_center_vx + search_radius_vx + 1)

                slices = tuple(slice(s, e) for s, e in zip(min_v, max_v))
                sub_volume = self.volume_grid[slices]

                density = np.mean(sub_volume) if sub_volume.size > 0 else 0

                if density < min_density:
                    min_density = density
                    best_pos = candidate_center_vx
                    if min_density == 0:  # Found a completely empty spot
                        break
            start_pos_vx = best_pos
        else:
            # Original behavior: pick one random spot
            start_pos_vx_xyz = self.rng.uniform(min_coords_nm, max_coords_nm) / self.resolution
            start_pos_vx = start_pos_vx_xyz[::-1].astype(int)

        radius_mean_vx = self.config["radius_mean"] / self.resolution
        radius_variability = self.config.get("radius_variability", 0.1)
        radius_std_vx = radius_mean_vx * radius_variability

        # Initial direction (randomized)
        theta = np.arccos(1 - 2 * self.rng.random())  # inclination
        phi = 2 * np.pi * self.rng.random()  # azimuth
        initial_direction_xyz = np.array([np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)])
        # Dampen the initial Z direction if specified
        if self.z_axis_dampening != 1.0:
            initial_direction_xyz[2] *= self.z_axis_dampening
            norm = np.linalg.norm(initial_direction_xyz)
            if norm > 0:
                initial_direction_xyz /= norm

        # List to hold all segments of the network
        all_centerline_vx = []
        all_radii1_vx = []
        all_radii2_vx = []

        # List of active branches to extend
        # Each element: (current_pos, current_dir_xyz, steps_left, current_radii)
        active_branches = [
            (
                start_pos_vx,
                initial_direction_xyz,
                num_steps,
                (self.rng.normal(radius_mean_vx, radius_std_vx), self.rng.normal(radius_mean_vx, radius_std_vx)),
            )
        ]

        # Store positions to avoid immediate re-branching from the same spot
        branch_origins = {tuple(start_pos_vx)}

        while active_branches:
            # Pop a branch to work on
            current_pos, current_dir_xyz, steps_left, current_radii = active_branches.pop(0)

            # Start a new segment for this branch
            centerline_segment = [current_pos]
            radii1_segment = [current_radii[0]]
            radii2_segment = [current_radii[1]]

            for step in range(steps_left):
                # Update radii
                r1_autocorr = max(self.radius_autocorrelation_r1, 1)  # Avoid division by zero
                r2_autocorr = max(self.radius_autocorrelation_r2, 1)  # Avoid division by zero

                r1 = radii1_segment[-1] + self.rng.normal(0, max(radii1_segment[-1], 1) / r1_autocorr) * step_size_vx
                r2 = radii2_segment[-1] + self.rng.normal(0, max(radii2_segment[-1], 1) / r2_autocorr) * step_size_vx

                min_r, max_r = radius_mean_vx / 4, radius_mean_vx * 2
                r1 = np.clip(r1, min_r, max_r)
                r2 = np.clip(r2, min_r, max_r)
                if r1 < r2 / 2:
                    r1 = r2 / 2
                if r2 < r1 / 2:
                    r2 = r1 / 2

                # Update direction with persistence
                if persistence_length_vx > 0:
                    # Small random perturbation to the direction vector
                    perturbation = self.rng.normal(size=3)
                    perturbation /= np.linalg.norm(perturbation)
                    # Scale perturbation by step size and persistence length
                    scale = step_size_vx / persistence_length_vx
                    current_dir_xyz = (1 - scale) * current_dir_xyz + scale * perturbation
                    current_dir_xyz /= np.linalg.norm(current_dir_xyz)

                # Dampen the Z direction component if specified
                if self.z_axis_dampening != 1.0:
                    current_dir_xyz[2] *= self.z_axis_dampening
                    norm = np.linalg.norm(current_dir_xyz)
                    if norm > 0:
                        current_dir_xyz /= norm

                direction_zyx = current_dir_xyz[::-1]
                new_pos = centerline_segment[-1] + direction_zyx * step_size_vx

                if not np.all((new_pos >= 0) & (new_pos < self.grid_dims)):
                    break

                centerline_segment.append(new_pos)
                radii1_segment.append(r1)
                radii2_segment.append(r2)

                # --- Branching Logic ---
                can_branch = self.enable_branching and (steps_left - step - 1 > 2)  # ensure branch has room to grow
                is_not_recent_origin = tuple(np.round(new_pos).astype(int)) not in branch_origins

                if can_branch and is_not_recent_origin and self.rng.random() < self.branch_prob_per_step:
                    branch_origins.add(tuple(np.round(new_pos).astype(int)))

                    # Create a new direction for the branch
                    branch_angle_rad = np.radians(
                        self.rng.normal(self.branch_angle_deg_mean, self.branch_angle_deg_std)
                    )

                    # Create a random axis of rotation perpendicular to the current direction
                    perp_vec = self.rng.normal(size=3)
                    perp_vec -= perp_vec.dot(current_dir_xyz) * current_dir_xyz
                    perp_vec /= np.linalg.norm(perp_vec)

                    # Rodrigues' rotation formula
                    new_dir = (
                        np.cos(branch_angle_rad) * current_dir_xyz
                        + np.sin(branch_angle_rad) * np.cross(perp_vec, current_dir_xyz)
                        + (1 - np.cos(branch_angle_rad)) * np.dot(perp_vec, current_dir_xyz) * perp_vec
                    )
                    new_dir /= np.linalg.norm(new_dir)

                    # Dampen the new branch's Z direction if specified
                    if self.z_axis_dampening != 1.0:
                        new_dir[2] *= self.z_axis_dampening
                        norm = np.linalg.norm(new_dir)
                        if norm > 0:
                            new_dir /= norm

                    # Split remaining steps
                    branch_steps = steps_left - step - 1

                    # Add new branch to the list to be processed
                    active_branches.append((new_pos, new_dir, branch_steps, (r1, r2)))

                    # The current branch terminates here to create the fork
                    break

            # Add the completed segment to the collection
            if len(centerline_segment) > 1:
                all_centerline_vx.append(np.array(centerline_segment))
                all_radii1_vx.append(np.array(radii1_segment))
                all_radii2_vx.append(np.array(radii2_segment))

        if not all_centerline_vx:
            return None, None, None

        # Combine all segments into a single array-like structure for processing
        # For simplicity, we concatenate them. This works because overlap check and voxelization
        # are done on the combined mask anyway.
        final_centerline = np.concatenate(all_centerline_vx)
        final_radii1 = np.concatenate(all_radii1_vx)
        final_radii2 = np.concatenate(all_radii2_vx)

        return final_centerline, final_radii1, final_radii2

    def _check_mito_in_bounds(self, centerline, radii1, radii2):
        """
        Checks if the entire mitochondrion surface is within the volume grid.
        """
        if centerline.shape[0] == 0:
            return True  # Should not happen with valid inputs

        # The ellipsoid extents are r1 for X/Y and r2 for Z
        # Z coords: centerline[:, 0], Y: centerline[:, 1], X: centerline[:, 2]
        min_bounds_zyx = np.array(
            [
                np.min(centerline[:, 0] - radii2),
                np.min(centerline[:, 1] - radii1),
                np.min(centerline[:, 2] - radii1),
            ]
        )
        max_bounds_zyx = np.array(
            [
                np.max(centerline[:, 0] + radii2),
                np.max(centerline[:, 1] + radii1),
                np.max(centerline[:, 2] + radii1),
            ]
        )

        in_bounds = np.all(min_bounds_zyx >= 0) and np.all(max_bounds_zyx < self.grid_dims)
        return in_bounds

    def generate(self):
        num_mitochondria = self.config["num_mitochondria"]
        all_points = []
        # Create an aggregated surface mask to store the surface of all mitochondria
        aggregated_surface_mask = np.zeros(self.grid_dims, dtype=np.bool_)
        # Create a list to store individual mitochondrion masks for instance segmentation
        instance_masks = []

        iterator = range(1, num_mitochondria + 1)
        if self.verbose:
            # print("Generating mitochondria using persistent random walk model...")
            iterator = tqdm(iterator, total=num_mitochondria, desc="Mitochondria")

        for mito_id in iterator:
            centerline, radii1, radii2 = None, None, None
            for attempt in range(self.max_generation_attempts):
                _centerline, _radii1, _radii2 = self._generate_single_mito_network()

                # Basic validation
                if _centerline is None or _centerline.shape[0] < 2:
                    continue  # Invalid centerline, try again

                # If clipping is disallowed, check if the mitochondrion is fully inside the volume
                if not self.allow_boundary_clipping:
                    if not self._check_mito_in_bounds(_centerline, _radii1, _radii2):
                        continue  # Mito is out of bounds, try again

                # A valid mitochondrion was generated
                centerline, radii1, radii2 = _centerline, _radii1, _radii2
                break  # Exit the retry loop

            # If all attempts failed, skip this mitochondrion
            if centerline is None:
                if self.verbose:
                    tqdm.write(
                        f"Skipping mitochondrion {mito_id} after failing to generate a valid one "
                        f"in {self.max_generation_attempts} attempts."
                    )
                continue

            current_mito_mask = np.zeros(self.grid_dims, dtype=np.bool_)

            for i in range(len(centerline)):
                center_vx = centerline[i].astype(int)
                r1_vx = max(1, radii1[i])
                r2_vx = max(1, radii2[i])

                ellipsoid_mask, slices = self._create_ellipsoid_mask(center_vx, r1_vx, r2_vx)
                current_mito_mask[slices] |= ellipsoid_mask

            # --- Overlap Check & Carving ---
            initial_volume = np.sum(current_mito_mask)
            if initial_volume == 0:
                if self.verbose:
                    tqdm.write(f"Skipping mitochondrion {mito_id} as it has zero initial volume.")
                continue

            # Temporarily carve to calculate overlap
            carved_mask = current_mito_mask & ~self.volume_grid
            final_volume = np.sum(carved_mask)

            # Check for excessive overlap
            max_overlap_ratio = self.config.get("max_overlap_ratio", 1.0)
            overlap_ratio = (initial_volume - final_volume) / initial_volume if initial_volume > 0 else 0

            if overlap_ratio > max_overlap_ratio:
                if self.verbose:
                    tqdm.write(
                        f"Skipping mitochondrion {mito_id} due to excessive overlap "
                        f"({overlap_ratio:.2%} > {max_overlap_ratio:.2%})."
                    )
                continue

            # The overlap is acceptable, so we use the carved mask from now on
            current_mito_mask = carved_mask

            if not np.any(current_mito_mask):
                if self.verbose:
                    tqdm.write(f"Skipping mitochondrion {mito_id} as it was fully carved out.")
                continue

            # Add the final, carved mask to the list of instance masks
            instance_masks.append(current_mito_mask)

            # Update global volume and label map
            self.volume_grid |= current_mito_mask
            self.label_map[current_mito_mask] = mito_id

            # --- Point Sampling ---
            # First, find the surface of the current mitochondrion
            eroded_mask = binary_erosion(current_mito_mask)
            surface_mask = current_mito_mask & ~eroded_mask

            # Add the current mitochondrion's surface to the aggregated mask
            aggregated_surface_mask |= surface_mask

            # --- Exclude surfaces touching the volume boundary from being sampled ---
            boundary_mask = np.zeros(self.grid_dims, dtype=np.bool_)
            boundary_mask[0, :, :] = True
            boundary_mask[-1, :, :] = True
            boundary_mask[:, 0, :] = True
            boundary_mask[:, -1, :] = True
            boundary_mask[:, :, 0] = True
            boundary_mask[:, :, -1] = True
            surface_mask[boundary_mask] = False

            fill_mitochondria = self.config.get("fill_mitochondria", False)
            final_sampling_mask = np.zeros(self.grid_dims, dtype=np.bool_)

            if not fill_mitochondria:
                # Sample from Surface Only
                sampling_prob = self.config.get("surface_sampling_prob", 0.5)
                rand_mask = self.rng.random(surface_mask.shape) < sampling_prob
                final_sampling_mask = surface_mask & rand_mask
            else:
                # Sample from both Surface and Interior with different probabilities
                interior_mask = eroded_mask  # The eroded part is the interior

                # 1. Sample the surface
                surface_prob = self.config.get("surface_sampling_prob", 0.5)
                surface_rand_mask = self.rng.random(surface_mask.shape) < surface_prob
                sampled_surface = surface_mask & surface_rand_mask

                # 2. Sample the interior
                interior_prob = self.config.get("voxel_sampling_prob", 0.1)
                interior_rand_mask = self.rng.random(interior_mask.shape) < interior_prob
                sampled_interior = interior_mask & interior_rand_mask

                # 3. Combine them
                final_sampling_mask = sampled_surface | sampled_interior

            # Get voxel indices of the final sampled points
            z_idx, y_idx, x_idx = np.nonzero(final_sampling_mask)
            if x_idx.size == 0:
                continue

            # Get labels for these points
            point_labels = self.label_map[z_idx, y_idx, x_idx]

            # Convert voxel indices to nm coordinates and add jitter
            jitter = self.rng.random((x_idx.size, 3)) - 0.5
            # Convert ZYX indices to XYZ points in nm
            points_nm = (np.vstack([x_idx, y_idx, z_idx]).T + jitter) * self.resolution

            points_with_ids = np.hstack([points_nm, point_labels[:, np.newaxis]])
            all_points.append(points_with_ids)

        if not all_points:
            final_points = np.empty((0, 4))
        else:
            final_points = np.concatenate(all_points, axis=0)

        # --- Apply Noise Models (similar to microtubule generator) ---

        # 1. Apply Localization Noise to mitochondria points
        if self.config.get("add_localization_noise", False) and final_points.size > 0:
            loc_precision = self.config.get("localization_precision", [8.0, 8.0, 15.0])
            if np.any(np.array(loc_precision) > 0):
                # Apply noise only to x, y, z coordinates
                points_coords = final_points[:, :3]
                noise = self.rng.normal(loc=0.0, scale=loc_precision, size=points_coords.shape)
                final_points[:, :3] = points_coords + noise

        # 2. Add Background Noise
        if self.config.get("add_background_noise", False) and final_points.size > 0:
            bg_density = self.config.get("background_noise_density", 0.0)
            if bg_density > 0:
                points_coords = final_points[:, :3]

                # Define volume bounds for noise generation.
                # XY plane uses the full padded volume.
                # Z axis is constrained by the extent of actual points within the padded volume.
                min_bounds_bg = -self.padding.copy().astype(float)
                max_bounds_bg = (self.dims + self.padding).copy().astype(float)

                min_bounds_bg[2] = np.maximum(np.min(points_coords[:, 2]), min_bounds_bg[2])
                max_bounds_bg[2] = np.minimum(np.max(points_coords[:, 2]), max_bounds_bg[2])

                # Ensure min < max to avoid issues with rng.uniform and volume calc
                if np.all(max_bounds_bg > min_bounds_bg):
                    volume_nm3 = np.prod(max_bounds_bg - min_bounds_bg)
                    num_bg_points = int(volume_nm3 * bg_density)

                    if num_bg_points > 0:
                        bg_points_coords = self.rng.uniform(
                            low=min_bounds_bg, high=max_bounds_bg, size=(num_bg_points, 3)
                        )
                        # Assign background points ID 0
                        bg_points_with_id = np.hstack([bg_points_coords, np.zeros((num_bg_points, 1))])
                        final_points = np.vstack([final_points, bg_points_with_id])

        # 3. Final clipping to ensure all points are within the padded volume
        if final_points.size > 0:
            min_bounds = -self.padding
            max_bounds = self.dims + self.padding
            in_bounds_x = (final_points[:, 0] >= min_bounds[0]) & (final_points[:, 0] < max_bounds[0])
            in_bounds_y = (final_points[:, 1] >= min_bounds[1]) & (final_points[:, 1] < max_bounds[1])
            in_bounds_z = (final_points[:, 2] >= min_bounds[2]) & (final_points[:, 2] < max_bounds[2])
            final_points = final_points[in_bounds_x & in_bounds_y & in_bounds_z]

        # --- Final Statistics ---
        num_requested = self.config["num_mitochondria"]
        # Count unique IDs > 0 for generated mitochondria
        unique_ids = np.unique(final_points[:, 3])
        num_generated = np.count_nonzero(unique_ids > 0)
        success_rate = num_generated / num_requested if num_requested > 0 else 0.0

        stats = {
            "generated_mitochondria": num_generated,
            "requested_mitochondria": num_requested,
            "total_points": final_points.shape[0],
            "success_rate": success_rate,
        }

        return final_points, stats, self.volume_grid, aggregated_surface_mask, instance_masks
