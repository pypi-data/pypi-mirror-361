# pylipextractor/pylipextractor/config.py

from pathlib import Path

class LipExtractionConfig:
    """
    Configuration for lip extraction and video processing parameters.
    """
    # --- Output frame dimensions ---
    IMG_H = 48 # Desired height for the output lip frames
    IMG_W = 96 # Desired width for the output lip frames
    MAX_FRAMES = None # Maximum frames to extract from a video. If None, extracts all frames.

    # --- Lip Cropping Settings ---
    # These margins are PROPORTIONAL to the tightly calculated lip bounding box.
    # Adjust these to expand/shrink the area around the detected lips.
    LIP_PROPORTIONAL_MARGIN_X = 0.25 # Horizontal margin as a proportion of lip width
    LIP_PROPORTIONAL_MARGIN_Y = 0.15 # Vertical margin as a proportion of lip height
    
    # These are fixed pixel paddings (applied AFTER proportional margins).
    # Use these for minor fine-tuning if needed.
    LIP_PADDING_LEFT_PX = 0
    LIP_PADDING_RIGHT_PX = 0
    LIP_PADDING_TOP_PX = 0
    LIP_PADDING_BOTTOM_PX = 0

    # --- General Processing Settings ---
    NUM_CPU_CORES = 5 # Number of CPU cores for parallel processing (if implemented in batch mode).
    # Renamed: Now represents max allowed percentage of ANY problematic frame (not just black)
    MAX_PROBLEMATIC_FRAMES_PERCENTAGE = 15.0 

    # Removed: SMOOTHING_WINDOW_SIZE is replaced by EMA_ALPHA for EMA smoothing
    # New: EMA Smoothing for Bounding Boxes
    APPLY_EMA_SMOOTHING: bool = True # Set to True to apply EMA smoothing to bounding box coordinates
    EMA_ALPHA: float = 0.3 # EMA smoothing factor (0.0 to 1.0, higher means less smoothing, 1.0 means no smoothing)

    # --- Debugging & Output Customization Settings ---
    DEBUG_OUTPUT_DIR = Path("./lip_extraction_debug") # Directory to save debug frames
    MAX_DEBUG_FRAMES = 20 # Maximum number of debug frames to save per video.
    SAVE_DEBUG_FRAMES = True # Set to True to save intermediate debug frames.
    
    # If True, MediaPipe lip landmarks will be drawn on the final extracted lip frames
    # (i.e., the frames saved in the .npy file and later converted to images).
    # This is for visualization/debugging of the final output, not typically for model training.
    INCLUDE_LANDMARKS_ON_FINAL_OUTPUT = False

    # --- Illumination and Contrast Normalization Settings (CLAHE) ---
    APPLY_CLAHE = True  # Set to True to apply CLAHE for illumination/contrast normalization
    CLAHE_CLIP_LIMIT = 2  # Threshold for contrast limiting (recommended: 1.0-4.0)
    CLAHE_TILE_GRID_SIZE = (4, 4) # Size of grid for histogram equalization (e.g., (8,8) or (16,16))

    # Black out non-lip areas within the cropped frame ---
    # If True, pixels outside the detected lip mask (within the bounding box) will be set to black.
    # This can help models focus exclusively on the lip region.
    BLACK_OUT_NON_LIP_AREAS = False

    # --- New FFmpeg Conversion Options ---
    CONVERT_TO_MP4_IF_NEEDED: bool = False  # Set to True to enable automatic conversion
    MP4_TEMP_DIR: Path = Path("temp_mp4_conversions") # Directory for temporary MP4 files
    # --- End New FFmpeg Conversion Options ---

    # --- Output Organization Settings (placeholder for future, currently no effect) ---
    DEFAULT_OUTPUT_BASE_DIR = Path("output_data") # Default directory for saving extracted NPYs
    ORGANIZE_OUTPUT_BY_VIDEO_NAME = True # If True, will save NPYs in subfolders based on video name


class MainConfig:
    """
    Main project configuration containing sub-configurations.
    """
    def __init__(self):
        self.lip_extraction = LipExtractionConfig()