# FramePerfect

A lightweight GUI application for precise frame-by-frame video analysis and screenshot extraction, built with PySide/PyQt and OpenCV.

## Why This Tool?

- **Perfect for**: Video editors, forensic analysts, researchers, and anyone needing precise frame analysis
- **Advantages over media players**: 
  - Guaranteed frame accuracy (no skipped frames)
  - Dedicated screenshot workflow
  - Clean interface without unnecessary features

## Key Features

- **Frame-accurate navigation**: Move through videos one frame at a time with perfect precision
- **Instant screenshot capture**: Save any frame as PNG/JPEG with customizable paths
- **Simple workflow**: Open -> Navigate -> Capture -> Repeat
- **Visual timeline**: Quickly jump to any frame using the position slider
- **Compatibility**: Supports Python 2+ and PyQt4/PyQt5/PyQt6/PySide/PySide2/PySide6

## Installation

```bash
pip install frameperfect
```

## Usage

```bash
python -m frameperfect
```

### Basic Workflow

1. Click "Open Video" and select your video file
2. Use these controls:
   - **Previous/Next Frame**: Move precisely through frames
   - **Slider**: Jump to any position in the video
   - **Save Frame**: Capture the current frame to your Pictures folder

## Troubleshooting

- If video doesn't open: Try converting to MP4 with H.264 codec
- For large videos: Consider splitting files for better performance

## Contributing

Contributions are welcome! Please submit pull requests or open issues on GitHub.

## License

AGPL-3.0 - See [LICENSE](LICENSE) for details.