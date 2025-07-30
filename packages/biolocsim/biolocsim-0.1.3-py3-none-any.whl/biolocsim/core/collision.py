import numpy as np


class VoxelGrid:
    """
    A voxel grid for detecting collisions in 3D space.
    Handles both isotropic (single float) and anisotropic (list/array of 3 floats) resolutions.
    """

    def __init__(self, dimensions, resolution):
        self.dimensions_nm = np.array(dimensions)

        if isinstance(resolution, (int, float)):
            self.resolution_nm = np.array([resolution, resolution, resolution], dtype=float)
        else:
            self.resolution_nm = np.array(resolution, dtype=float)

        if self.resolution_nm.shape != (3,):
            raise ValueError("Resolution must be a single number or a list/array of 3 numbers.")

        self.grid_shape = np.ceil(self.dimensions_nm / self.resolution_nm).astype(int)
        self.grid_shape[self.grid_shape < 1] = 1
        self.grid = np.zeros(self.grid_shape, dtype=bool)

    def _to_grid_coords(self, points_nm):
        """Convert world coordinates (nm) to grid indices."""
        return (points_nm / self.resolution_nm).astype(int)

    def add_curve(self, centerline_points_nm, radius_nm):
        """
        Marks the voxels occupied by a curve with a given radius (or radii) as True.
        This method now supports a variable radius along the centerline.
        """
        if centerline_points_nm.size == 0:
            return

        # Convert all points to grid coordinates at once
        points_grid = (centerline_points_nm / self.resolution_nm).astype(int)

        # Handle both scalar and array radii
        is_scalar_radius = isinstance(radius_nm, (int, float))
        if is_scalar_radius:
            radii_grid = (radius_nm / self.resolution_nm).astype(int)
        else:
            # Ensure radius_nm is a column vector for broadcasting
            radii_nm_col = radius_nm[:, np.newaxis]
            radii_grid = (radii_nm_col / self.resolution_nm).astype(int)

        for i, point in enumerate(points_grid):
            radius_vector = radii_grid if is_scalar_radius else radii_grid[i]

            # Define the bounding box for the sphere/ellipsoid around the point
            min_bounds = np.maximum(0, point - radius_vector)
            max_bounds = np.minimum(self.grid_shape, point + radius_vector + 1)

            # Create a meshgrid for the bounding box
            x, y, z = np.meshgrid(
                np.arange(min_bounds[0], max_bounds[0]),
                np.arange(min_bounds[1], max_bounds[1]),
                np.arange(min_bounds[2], max_bounds[2]),
                indexing="ij",
            )

            # Calculate distance from the center point, normalized by radius
            # This forms an ellipsoidal check for anisotropic resolutions
            dist_sq = (
                ((x - point[0]) / (radius_vector[0] + 1e-9)) ** 2
                + ((y - point[1]) / (radius_vector[1] + 1e-9)) ** 2
                + ((z - point[2]) / (radius_vector[2] + 1e-9)) ** 2
            )

            # Mark all voxels within the ellipsoid as occupied
            self.grid[x[dist_sq <= 1], y[dist_sq <= 1], z[dist_sq <= 1]] = True

    def check_collision(self, points_nm, radius_nm):
        """
        Check if a given curve collides with occupied voxels in the grid.

        Args:
            points_nm (np.ndarray): A set of points defining the curve, with shape (N, 3).
            radius_nm (float): The radius of the curve in nm.

        Returns:
            list[int]: A list of indices of colliding points. An empty list means no collision.
        """
        colliding_indices = []
        radius_grid = (radius_nm / self.resolution_nm).astype(int)

        for i, point_nm in enumerate(points_nm):
            grid_coords = self._to_grid_coords(point_nm)

            # Check if the point is within the boundary
            if np.any(grid_coords < 0) or np.any(grid_coords > self.grid_shape):
                colliding_indices.append(i)
                continue  # Treat as collision with the boundary

            min_bounds = np.maximum(0, grid_coords - radius_grid)
            max_bounds = np.minimum(self.grid_shape, grid_coords + radius_grid + 1)

            slices = tuple(slice(min_b, max_b) for min_b, max_b in zip(min_bounds, max_bounds))

            if np.any(self.grid[slices]):
                colliding_indices.append(i)
        return colliding_indices

    def get_repulsion_vector(self, point_nm, radius_nm=0):
        """
        Calculate a repulsion vector for a point away from occupied voxels.
        The vector points from the centroid of occupied voxels to the point.
        """
        grid_coords = self._to_grid_coords(point_nm)
        radius_grid = (radius_nm / self.resolution_nm).astype(int)

        min_bounds = np.maximum(0, grid_coords - radius_grid)
        max_bounds = np.minimum(self.grid_shape, grid_coords + radius_grid + 1)

        slices = tuple(slice(min_b, max_b) for min_b, max_b in zip(min_bounds, max_bounds))

        local_grid = self.grid[slices]
        occupied_indices = np.argwhere(local_grid)

        if occupied_indices.size == 0:
            return np.zeros(3)

        # Convert local indices to global grid indices
        global_occupied_indices = occupied_indices + np.array([s.start for s in slices])
        # Convert global grid indices to world coordinates (nm)
        occupied_world_coords = global_occupied_indices * self.resolution_nm
        centroid = np.mean(occupied_world_coords, axis=0)

        repulsion_vector = point_nm - centroid
        norm = np.linalg.norm(repulsion_vector)
        if norm > 0:
            repulsion_vector /= norm

        return repulsion_vector
