# vidcii

vidcii is a small Python CLI that turns video files into ASCII art.

It can either:
1. play a video live inside the terminal, or
2. export the video as a new ASCII-styled video file.

## What the Project Is

This is a Python CLI application that opens any standard video file, processes its frames sequentially in real-time, maps pixel intensities to ASCII characters, and draws them directly into the terminal or renders them into a file.

## Why it Exists

`vidcii` was created as a creative learning project to explore real-time video processing and command-line interfaces. It is designed to be lightweight, easy to understand, and explainable, with minimal external dependencies.

## Features

- Play videos inside the terminal as ASCII art
- Export videos into ASCII-styled `.mp4` files
- Optional ANSI color mode
- Optional best-effort audio playback with `ffplay` or `mpv`
- Simple and dense ASCII character sets
- Invert brightness mapping
- Adjustable width and FPS

## Installation

To set up and run `vidcii` locally:

1. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage Examples

```bash
# Play video in the terminal
python3 vidcii.py video.mp4

# Play with color
python3 vidcii.py video.mp4 --color

# Play with best-effort audio
python3 vidcii.py video.mp4 --audio --audio-backend ffplay

# Export video as ASCII-styled MP4 (Default 1280x720)
python3 vidcii.py video.mp4 --export ascii_output.mp4

# HD export (1920x1080)
python3 vidcii.py video.mp4 --export ascii_output.mp4 --export-preset hd

# Custom export size in pixels
python3 vidcii.py video.mp4 --export ascii_output.mp4 --export-width 1920 --export-height 1080

# Color HD export
python3 vidcii.py video.mp4 --export ascii_output.mp4 --color --export-preset hd

# Export with custom font scale and cell spacing
python3 vidcii.py video.mp4 --export ascii_output.mp4 --font-scale 0.5 --cell-width 10 --cell-height 15
```

### Optional V1 Customizations:
- **Set Specific Character Width and Frame Rate**:
  ```bash
  python3 vidcii.py path/to/video.mp4 --width 80 --fps 15
  ```
- **Use Dense Character Mapping and Inverted Colors**:
  ```bash
  python3 vidcii.py path/to/video.mp4 --charset dense --invert
  ```

---

## Required External Tools for Audio
To use `--audio`, one of the following players must be installed on your system:
- **mpv** (default backend)
- **ffplay** (from ffmpeg)

### Linux Install Examples:
```bash
sudo apt install mpv
sudo apt install ffmpeg
```

---

## Export limitations and considerations

The export mode writes a new ASCII-styled video file using OpenCV.

Current limitations and details:
- **No Audio Track**: Exported videos do not include the original audio track yet.
- **Export Resolution and Performance**: Higher export resolutions (like HD) take longer to render.
- **Color Export Performance**: Color export (using RGB color sampling for each character) is slower than grayscale export.
- **ASCII Density**: Using a very dense character set or width increases render times.
- **Quality Parameters**: Render quality and character alignment depend on options like font size (`--font-scale`), cell dimensions (`--cell-width` / `--cell-height`), and width.

---

## General Limitations

* **Best-Effort Audio Sync**: In terminal play mode, audio synchronization is approximate and best-effort.
* **Terminal Speed Affects Sync**: Slow terminal rendering or large window sizes can cause the video to lag behind the audio in live playback.
* **Color Mode Performance**: Rendering in color in the terminal is slower than grayscale.
* **TrueColor Support**: Not all terminal emulators support TrueColor (`\033[38;2;R;G;Bm`).
* **No Playback Controls**: There are no playback controls (play, pause, fast forward) during playback yet.

## Roadmap

- [x] **Color Mode**: TrueColor ANSI rendering mode.
- [x] **Audio Support**: Synchronized audio playback using mpv and ffplay backends.
- [ ] **Export to Text Animation**: Output ASCII frames to a file format (e.g. HTML or text sequence).
- [ ] **Webcam Mode**: Feed live webcam video directly to the terminal.
- [ ] **Unicode Block Rendering**: High-fidelity block rendering (`▄`, `▀`, `█`).
