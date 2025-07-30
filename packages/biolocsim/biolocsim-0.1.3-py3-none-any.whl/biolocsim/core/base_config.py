# This basic configuration is used for testing and development.
# It is not used for the main application.

# fmt: off
# --- Microtubule Generator Configuration ---
MT_CONFIG = {
    "seed"            : 42,
    "volume_dims"     : [25000, 25000, 3000],       # (x, y, z) dimensions of the simulation volume in nm
    "padding"         : [0, 0, 150],                # Padding around the volume in nm
    "resolution"      : 200,                        # Voxel size in nm (isotropic)
    "num_tubes"       : 1,
    "tube_radius"     : 12.5,                       # Radius of the microtubule cylinder in nm (actual is ~12.5nm)
    "collision_radius": 13,                         # A slightly larger radius for collision to ensure separation in nm

    # --- B-Spline generation parameters ---
    "generate_on_boundary"      : True,     # If True, start/end points are on the boundary. Otherwise, random.
    "generation_mode"           : "corner", # Generation mode for start/end points. Options: "random", "center", "corner"
    "control_points_range"      : [4, 6],   # Min/max number of control points for each spline
    "min_control_point_angle"   : 50,       # (Degrees) Min angle between control point segments to avoid sharp turns
    "min_control_point_distance": 100,      # (nm) Min distance between consecutive control points
    "spline_degree"             : 2,        # B-spline degree (k), e.g., 2 for quadratic, 3 for cubic
    "smoothness"                : 200,      # B-spline smoothness parameter
    "centerline_point_spacing"  : 200.0,    # Spacing between points on the centerline (in nm)
    "centerline_sampling_points": 100,      # Number of points for over-sampling to calculate length

    # --- Surface point cloud generation ---
    "surface_points_per_sample": 3, # Number of points to generate around each centerline sample

    # --- Generation process ---
    "max_attempts_per_tube"  : 10,  # Max attempts to generate a single tube
    "max_adjustment_attempts": 10,  # Max attempts to fix a single tube's path
    "adjustment_step"        : 200, # How much to move a control point during adjustment (in nm)

    # --- Noise Parameters ---
    "add_surface_jitter"              : True,
    "surface_jitter_along_tangent_std": 3.0,  # (nm) Std dev for jitter along the tangent
    "add_localization_noise"          : True,
    # (nm) [x, y, z] std dev for localization error. Can be a single value for isotropic noise.
    "localization_precision"          : [5.0, 5.0, 10.0],
    "add_background_noise"            : True,
    # Density of noise points per nm^3. e.g., 1e-6 means 1 point per 1,000,000 nm^3.
    "background_noise_density"        : 1e-9,
}

# --- Mitochondria Generator Configuration ---
MITO_CONFIG = {
    "seed"            : 42,
    "volume_dims"     : [20000, 20000, 2500],       # (x, y, z) dimensions in nm
    "padding"         : [0, 0, 100],                # Padding around the volume in nm
    "num_mitochondria": 1,
    "resolution"      : 40,                         # Voxel size in nm (smaller is higher res but slower)

    # --- Mitochondria Shape Parameters ---
    "length_mean"         : 1000, # Mean length of a mitochondrion in nm (actual is 2-6 um)
    "length_heterogeneity": 0.1,  # Variability in length (0 to 1)
    "persistence_length"  : 1000, # Controls the straightness of the mitochondrion
    "step_size"           : 50,   # Step size of the random walk in nm (actual is ~50 nm)
    "radius_mean"         : 500,  # Mean radius of the mitochondrion tube in nm (actual is 200-500 nm)
    "radius_variability"  : 0.1,  # Variability of the radius (0 to 1)

    # --- Walk Behavior Parameters ---
    # Dampens vertical (Z-axis) movement to make mitochondria flatter.
    # 1.0 = isotropic (moves equally in all directions).
    # 0.0 = 2D walk (moves only in XY plane).
    # Values < 1.0 are recommended for thin volumes.
    "z_axis_dampening": 0.1,

    # --- Radius Dynamics Parameters ---
    # Controls how much the radius varies along the length of the mitochondrion.
    # Smaller values lead to more pronounced, faster changes in thickness (rougher).
    # Larger values lead to smoother, more gradual changes in thickness.
    "radius_autocorrelation_r1": 40.0, # Default: 60
    "radius_autocorrelation_r2": 25.0, # Default: 30

    # --- Branching Parameters ---
    "enable_branching"     : True, # Set to True to allow mitochondrial branching
    "branch_prob_per_step" : 0.05, # Probability of a branch occurring at each step
    "branch_angle_deg_mean": 45,   # Mean angle of the new branch in degrees
    "branch_angle_deg_std" : 10,   # Std dev of the new branch angle in degrees

    # --- Voxel-based generation parameters ---
    "surface_sampling_prob"      : 0.8,   # Probability of keeping a surface voxel, which is used to sample points from the surface
    "fill_mitochondria"          : True,  # If True,  sample points from the entire volume, not just the surface
    "voxel_sampling_prob"        : 0.01,  # Probability of keeping an internal voxel (if fill_mitochondria is True)
    "max_overlap_ratio"          : 0.5,   # Maximum allowed overlap ratio before a mitochondrion is discarded
    "allow_boundary_clipping"    : False, # If False, mitochondria must be fully within the volume
    "max_generation_attempts"    : 10,    # Max retries per mitochondrion if it goes out of bounds
    "start_pos_search_candidates": 10,    # Number of candidate positions to sample around the center
    "start_pos_search_radius_nm" : 800,   # Radius around the center to search for candidate positions (unit: nm)

    # --- Noise Parameters ---
    "add_localization_noise"  : True,
    # (nm) [x, y, z] std dev for localization error. Can be a single value for isotropic noise.
    "localization_precision"  : [8.0, 8.0, 15.0],
    "add_background_noise"    : True,
    # Density of noise points per nm^3. e.g., 1e-6 means 1 point per 1,000,000 nm^3.
    "background_noise_density": 1e-9,
}
# fmt: on
