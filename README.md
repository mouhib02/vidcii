# vidcii

vidcii is a small Python CLI that turns video files into ASCII art.

It can play a video live inside the terminal, render optional ANSI color, play best-effort audio through an external backend, and export the result as a new ASCII-styled video file.

It is not meant to be a serious media player. It is a compact project for learning about video frames, terminal rendering, timing, and export pipelines.

## Demo

![vidcii demo](assets/vidcii-demo.gif)

The demo shows:

- live ASCII playback in the terminal
- optional color rendering
- HD export mode
- the exported ASCII-styled video result

## What it does

vidcii has two main modes.

### 1. Terminal playback

Read a video file frame by frame and redraw it in the terminal as ASCII characters.

```bash
python vidcii.py video.mp4
```

Useful options:

```bash
python vidcii.py video.mp4 --width 80 --fps 15
python vidcii.py video.mp4 --charset dense
python vidcii.py video.mp4 --invert
python vidcii.py video.mp4 --color
```

### 2. ASCII video export

Render the ASCII output into a new `.mp4` file.

```bash
python vidcii.py video.mp4 --export ascii_output.mp4
```

HD export:

```bash
python vidcii.py video.mp4 --export ascii_output.mp4 --export-preset hd
```

Color HD export:

```bash
python vidcii.py video.mp4 --export ascii_output.mp4 --export-preset hd --color
```

Export mode creates a new video file with ASCII characters drawn onto a real canvas. It does not depend on terminal size.

## Features

- Play videos inside the terminal as ASCII art
- Export videos as ASCII-styled `.mp4` files
- Optional ANSI true-color terminal rendering
- Optional best-effort audio playback using `ffplay` or `mpv`
- Simple and dense character sets
- Invert brightness mapping
- Adjustable playback width and FPS
- Export presets: `small`, `medium`, `hd`
- Custom export size, font scale, font thickness, and cell spacing

## Installation

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Requirements

Python dependency:

```text
opencv-python
```

Optional audio backends:

- `ffplay`, included with FFmpeg
- `mpv`

Audio playback is optional. The tool still works without them.

## Usage

Basic playback:

```bash
python vidcii.py video.mp4
```

Set playback width and FPS:

```bash
python vidcii.py video.mp4 --width 100 --fps 15
```

Use dense ASCII characters:

```bash
python vidcii.py video.mp4 --charset dense
```

Invert brightness:

```bash
python vidcii.py video.mp4 --invert
```

Use terminal color:

```bash
python vidcii.py video.mp4 --color
```

Play with best-effort audio:

```bash
python vidcii.py video.mp4 --audio --audio-backend ffplay
```

Export an ASCII-styled video:

```bash
python vidcii.py video.mp4 --export ascii_output.mp4
```

Export in HD:

```bash
python vidcii.py video.mp4 --export ascii_output.mp4 --export-preset hd
```

Export in color HD:

```bash
python vidcii.py video.mp4 --export ascii_output.mp4 --export-preset hd --color
```

## Export options

```bash
--export OUTPUT_PATH
--export-preset small|medium|hd
--export-width 1280
--export-height 720
--font-scale 0.45
--font-thickness 1
--cell-width 8
--cell-height 12
```

Default export size:

```text
medium: 1280x720
```

Presets:

```text
small  = 854x480
medium = 1280x720
hd     = 1920x1080
```

Manual export width and height override the preset.

## How it works

vidcii reads frames from a video using OpenCV.

For each frame:

1. resize the frame
2. convert brightness into ASCII characters
3. optionally sample color from the original frame
4. either draw the frame in the terminal or render it onto a video canvas

The export path is separate from live playback. Terminal playback is optimized for screen output. Export mode is optimized for creating a clearer video file.

## Limitations

- Exported videos do not include the original audio track yet
- Audio playback during live mode is best-effort
- Terminal rendering speed affects live playback smoothness
- Color mode is slower than grayscale mode
- HD export takes longer than small or medium export
- True-color output depends on terminal support
- This is not a professional media player


MIT
