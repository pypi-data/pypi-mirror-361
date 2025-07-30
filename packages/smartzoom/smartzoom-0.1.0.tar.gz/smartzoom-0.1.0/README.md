# SmartZoom

A Python utility to automatically apply a smooth, continuous zoom to a video, perfectly framing its content.

![PyPI Version](https://img.shields.io/pypi/v/smartzoom.svg?style=flat-square)
![License](https://img.shields.io/pypi/l/smartzoom.svg?style=flat-square)

---

This tool solves a common problem for video creators: adding a subtle, engaging "Ken Burns" style zoom to static shots (like presentations, code tutorials, or talking-head videos) without manual editing. It intelligently detects the subject of your video, calculates the optimal framing, and renders a new high-quality video with a perfectly smooth zoom.

![Demonstration of smartzoom](readme.gif)

### Key Features

-   **Automatic Content Detection:** Intelligently finds the bounding box of all non-background content on the first frame.
-   **Perfectly Centered Zoom:** The zoom is always mathematically centered on your content.
-   **Smooth, Constant Motion:** A linear zoom is applied throughout the video's duration, ensuring no stutter or jitter.
-   **Aspect Ratio Correction:** The final framing is guaranteed to match the video's aspect ratio (e.g., 16:9), providing a "what you see is what you get" result.
-   **High-Quality Output:** The original audio is copied without re-encoding, preserving its quality completely.
-   **Built-in Debug Mode:** Generate visual aids to see exactly what the detection algorithm is doing before rendering the full video.

## Installation

This package requires Python 3.8+ and FFmpeg.

**1. Install FFmpeg:**
You must have FFmpeg installed on your system and accessible from your PATH. You can download it from the official website: [ffmpeg.org](https://ffmpeg.org/download.html)

**2. Install the Package:**
Install `smartzoom` using pip:

```bash
pip install smartzoom
```

This will also install its Python dependencies, `opencv-python` and `numpy`.

## Usage

### As a Python Library

Using the library is straightforward. Import the package and call it directly with your input and output paths.

```python
import smartzoom

smartzoom('input_video.mp4', 'output.mp4', margin=50, debug=True)
```

or

```python
import smartzoom
import os

# Define your input and output files
input_video = 'my_presentation.mp4'
output_folder = 'processed_videos'
output_video = os.path.join(output_folder, 'my_presentation_zoomed.mp4')

# Create the output directory if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Run the smart zoom function
smartzoom(
    input_path=input_video,
    output_path=output_video,
    margin=50,  # Set a 50px margin around the detected content
    debug=True  # Set to True to save detection images in the output folder
)

print(f"Processing complete! Check '{output_video}'")
```
## API Reference

The package provides one primary public function.

```python
smartzoom(
    input_path: str,
    output_path: str,
    margin: int = 50,
    debug: bool = False
)
```

**Parameters:**

-   `input_path` (str):
    Path to the source video file.

-   `output_path` (str):
    Path where the final video will be saved. The output directory will be created if it doesn't exist.

-   `margin` (int, optional):
    The pixel distance to keep from the detected content on all sides. Defaults to `50`.

-   `debug` (bool, optional):
    If `True`, saves two visualization images (`debug_raw_viewport.png` and `debug_margin_viewport.png`) to the output folder to show the detection results. Defaults to `False`.

## How It Works

1.  **Analyze Frame:** The script reads the first frame of the input video.
2.  **Detect Content:** It converts the frame to grayscale and uses a binary threshold to isolate all light-colored content from the dark background.
3.  **Find Bounding Box:** It finds the single bounding box that encloses all detected content.
4.  **Calculate Viewport:** It adds the specified `margin` and then expands this box to match the video's 16:9 aspect ratio. This becomes the final "target viewport".
5.  **Determine Zoom:** It calculates the zoom multiplier required to make the target viewport fill the entire screen.
6.  **Render Video:** It processes the video frame-by-frame, applying a linear zoom from 1.0x to the final calculated zoom value.
7.  **Add Audio:** It uses FFmpeg to losslessly copy the audio stream from the original video and merge it with the newly rendered video frames.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
