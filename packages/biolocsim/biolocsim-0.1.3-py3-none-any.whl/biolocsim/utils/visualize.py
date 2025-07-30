from typing import Union

import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage


def plot_top_down_view(
    points: np.ndarray,
    volume_dims: Union[list, int, float],
    padding: Union[list, int, float],
    output_path: str,
    dpi: int = 300,
    sample_ratio: float = 1.0,
    dot_size: float = 1.0,
):
    """
    Generates a top-down view of the 3D point cloud, colors it by Z-depth,
    and saves it as an image file without borders or axes.

    Args:
        points (np.ndarray): A NumPy array of shape (N, 3) representing the point cloud.
        volume_dims (Union[list, int, float]): A list or tuple of 3 elements representing the volume
                            dimensions [x, y, z] to set the plot limits. If a single number is provided,
                            it is assumed to be a cube and the volume dimensions are set to [x, x, x].
        padding (Union[list, int, float]): Padding around the volume in nm. If a single number is provided,
                            it is assumed to be a cube and the padding is set to [p, p, p].
        output_path (str): The path to save the output image.
        dpi (int): The resolution of the saved image in dots per inch.
        sample_ratio (float): The fraction of points to display. Defaults to 1.0 (all points).
        dot_size (float): The size of the dots in the scatter plot.
    """
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError("Point cloud must be an array of shape (N, 3).")

    if isinstance(volume_dims, (int, float)):
        volume_dims = np.array([volume_dims, volume_dims, volume_dims])
    elif len(volume_dims) != 3:
        raise ValueError("volume_dims must have 3 elements (x, y, z).")
    else:
        volume_dims = np.array(volume_dims)

    if isinstance(padding, (int, float)):
        padding = np.array([padding, padding, padding])
    elif len(padding) != 3:
        raise ValueError("padding must have 3 elements (x, y, z).")
    else:
        padding = np.array(padding)

    # Subsample points for performance if needed
    num_points = points.shape[0]
    if 0 < sample_ratio < 1.0:
        sample_size = int(num_points * sample_ratio)
        indices = np.random.choice(num_points, sample_size, replace=False)
        sampled_points = points[indices]
    else:
        sampled_points = points

    x = sampled_points[:, 0]
    y = sampled_points[:, 1]
    z = sampled_points[:, 2]

    # Set figure size to match the aspect ratio of the volume's X and Y dimensions
    fig_width = 10  # inches
    data_aspect_ratio = (volume_dims[1] + 2 * padding[1]) / (volume_dims[0] + 2 * padding[0])
    fig_height = fig_width * data_aspect_ratio

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    # Create the scatter plot, colored by Z
    scatter = ax.scatter(
        x,
        y,
        c=z,
        s=dot_size,
        cmap="jet",
        marker=".",
        vmin=-padding[2],
        vmax=volume_dims[2] + padding[2],
    )

    # Add color bar and label its start and end points
    cbar = fig.colorbar(scatter, ax=ax)
    cbar.set_label("Z-depth (nm)")
    z_lims = [-padding[2], volume_dims[2] + padding[2]]
    cbar.set_ticks(z_lims)
    cbar.ax.set_yticklabels([f"{z_lims[0]:.0f}", f"{z_lims[1]:.0f}"])

    # Set plot limits
    x_lims = [-padding[0], volume_dims[0] + padding[0]]
    y_lims = [-padding[1], volume_dims[1] + padding[1]]
    ax.set_xlim(x_lims)
    ax.set_ylim(y_lims)

    # Invert the y-axis to place the origin at the top-left corner
    # ax.invert_yaxis()

    # Set axis labels and ticks
    ax.set_xlabel("X (nm)")
    ax.set_ylabel("Y (nm)")
    ax.set_xticks(x_lims)
    ax.set_yticks(y_lims)
    ax.set_aspect("equal", adjustable="box")

    # Save the figure
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)  # Close the figure to free up memory

    print(f"Top-down view saved to {output_path}")


def render_centerlines(
    centerlines,
    volume_dims,
    padding,
    mask_radius,
    render_psf_sigma_nm,
    final_pixel_size_nm,
    return_type="2d",
    output_dtype=np.uint16,
    binary_mask=False,
):
    """
    Renders centerlines into a 2D image or 3D volume with anti-aliasing.

    This function renders each centerline segment as a thick line on a 2D/3D grid.
    To achieve smooth, anti-aliased lines, it calculates pixel intensity
    based on the distance from the centerline when `binary_mask` is False.

    Args:
        centerlines (list of np.ndarray): List of centerline point clouds.
        volume_dims (list or np.ndarray): The dimensions of the simulation volume [x, y, z].
        padding (list or np.ndarray): The padding around the volume [x, y, z].
        mask_radius (float): The radius of the tube for rendering purposes (in nm).
        render_psf_sigma_nm (float): The sigma of the Gaussian PSF to apply (in nm).
        final_pixel_size_nm (float): The size of a pixel/voxel in the final output image (in nm).
        return_type (str): The type of output to generate, either "2d" or "3d".
        output_dtype (type): The NumPy data type for the final output image.
        binary_mask (bool): If True, creates a binary mask (pixels are 0 or 1) with hard edges.
                            If False, generates an anti-aliased image with smooth edges
                            based on pixel distance from the centerline. Defaults to False.
    """
    # Use the final pixel size directly, as supersampling is replaced
    effective_pixel_size = final_pixel_size_nm

    padded_dims = np.array(volume_dims) + 2 * np.array(padding)
    inv_pixel_size = 1.0 / effective_pixel_size
    radius_pixels = mask_radius / effective_pixel_size
    radius_pixels_sq = radius_pixels**2

    if isinstance(output_dtype, str):
        output_dtype = np.dtype(output_dtype)

    if return_type == "3d":
        output_dims_pixels = tuple(np.ceil(padded_dims[::-1] / effective_pixel_size).astype(int))  # Z, Y, X
        rendered_image = np.zeros(output_dims_pixels, dtype=np.float32)

        for centerline in centerlines:
            if centerline.shape[0] < 2:
                continue

            # Convert all points to padded pixel coordinates at once
            centerline_pixels = (centerline + padding) * inv_pixel_size

            for i in range(len(centerline_pixels) - 1):
                p1_px = centerline_pixels[i]  # X, Y, Z
                p2_px = centerline_pixels[i + 1]  # X, Y, Z

                # Vector from p1 to p2
                v = p2_px - p1_px
                len_sq = np.dot(v, v)

                # Define bounding box for the line segment with radius
                min_coords = np.minimum(p1_px, p2_px) - radius_pixels
                max_coords = np.maximum(p1_px, p2_px) + radius_pixels

                # Convert to integer pixel indices and clamp to image boundaries
                start_indices = np.maximum(0, np.floor(min_coords)).astype(int)
                end_indices = np.minimum(
                    np.array(rendered_image.shape)[::-1] - 1,  # image shape is Z,Y,X, so reversed is X,Y,Z
                    np.ceil(max_coords),
                ).astype(int)

                start_x, start_y, start_z = start_indices
                end_x, end_y, end_z = end_indices

                if start_x > end_x or start_y > end_y or start_z > end_z:
                    continue

                # Iterate over pixels in the bounding box
                for z_px in range(start_z, end_z + 1):
                    for y_px in range(start_y, end_y + 1):
                        for x_px in range(start_x, end_x + 1):
                            # Voxel center (X, Y, Z)
                            p = np.array([x_px + 0.5, y_px + 0.5, z_px + 0.5])

                            if len_sq == 0:  # p1 and p2 are the same point
                                dist_sq = np.dot(p - p1_px, p - p1_px)
                            else:
                                # Project p onto the line containing the segment
                                t = np.dot(p - p1_px, v) / len_sq
                                t = np.clip(t, 0, 1)  # Clamp t to be on the segment
                                projection = p1_px + t * v
                                dist_sq = np.dot(p - projection, p - projection)

                            if dist_sq <= radius_pixels_sq:
                                if binary_mask:
                                    rendered_image[z_px, y_px, x_px] = 1.0
                                else:
                                    # Anti-aliasing: Value is proportional to distance from center
                                    value = 1.0 - (dist_sq / radius_pixels_sq)
                                    rendered_image[z_px, y_px, x_px] = max(rendered_image[z_px, y_px, x_px], value)

    elif return_type == "2d":
        output_dims_pixels = (
            int(np.ceil(padded_dims[1] / effective_pixel_size)),  # height (Y)
            int(np.ceil(padded_dims[0] / effective_pixel_size)),  # width (X)
        )
        rendered_image = np.zeros(output_dims_pixels, dtype=np.float32)

        for centerline in centerlines:
            if centerline.shape[0] < 2:
                continue

            # Convert all points to padded pixel coordinates at once, taking only X and Y
            centerline_pixels = (centerline[:, :2] + padding[:2]) * inv_pixel_size

            for i in range(len(centerline_pixels) - 1):
                p1_px = centerline_pixels[i]
                p2_px = centerline_pixels[i + 1]

                # Vector from p1 to p2
                v = p2_px - p1_px
                len_sq = np.dot(v, v)

                # Define bounding box for the line segment with radius
                min_x = min(p1_px[0], p2_px[0]) - radius_pixels
                max_x = max(p1_px[0], p2_px[0]) + radius_pixels
                min_y = min(p1_px[1], p2_px[1]) - radius_pixels
                max_y = max(p1_px[1], p2_px[1]) + radius_pixels

                # Convert to integer pixel indices and clamp to image boundaries
                start_x = max(0, int(np.floor(min_x)))
                end_x = min(output_dims_pixels[1] - 1, int(np.ceil(max_x)))
                start_y = max(0, int(np.floor(min_y)))
                end_y = min(output_dims_pixels[0] - 1, int(np.ceil(max_y)))

                if start_x > end_x or start_y > end_y:
                    continue

                # Iterate over pixels in the bounding box
                for y_px in range(start_y, end_y + 1):
                    for x_px in range(start_x, end_x + 1):
                        # Pixel center
                        p = np.array([x_px + 0.5, y_px + 0.5])

                        if len_sq == 0:  # p1 and p2 are the same point
                            dist_sq = np.dot(p - p1_px, p - p1_px)
                        else:
                            # Project p onto the line containing the segment
                            t = np.dot(p - p1_px, v) / len_sq
                            t = np.clip(t, 0, 1)  # Clamp t to be on the segment

                            # Projection point
                            projection = p1_px + t * v

                            # Distance squared from pixel center to projection on segment
                            dist_sq = np.dot(p - projection, p - projection)

                        if dist_sq <= radius_pixels_sq:
                            if binary_mask:
                                # Image is indexed (Y, X)
                                rendered_image[y_px, x_px] = 1.0
                            else:
                                # Anti-aliasing: Value is proportional to distance from center
                                value = 1.0 - (dist_sq / radius_pixels_sq)
                                rendered_image[y_px, x_px] = max(rendered_image[y_px, x_px], value)
    else:
        raise ValueError(f"Invalid return_type: '{return_type}'. Must be '2d' or '3d'.")

    # Apply Gaussian PSF to the final-sized image
    if render_psf_sigma_nm > 0:
        # PSF sigma is relative to the final pixel size, not the effective (supersampled) one
        psf_sigma_pixels = render_psf_sigma_nm / final_pixel_size_nm
        # print(f"Applying Gaussian PSF with sigma={psf_sigma_pixels:.2f} pixels...")
        rendered_image = ndimage.gaussian_filter(rendered_image, sigma=psf_sigma_pixels)

    # Normalize and convert to output dtype
    max_val = np.max(rendered_image)
    if max_val > 0:
        rendered_image /= max_val

    if np.issubdtype(output_dtype, np.integer):
        max_int = np.iinfo(output_dtype).max
        final_image = (rendered_image * max_int).astype(output_dtype)
    else:
        final_image = rendered_image.astype(output_dtype)

    return final_image
