# vidcii Examples

This folder contains tips, usage patterns, and guidelines on how to get the most out of `vidcii`.

vidcii is a small Python CLI that turns video files into ASCII art.

It can either:
1. play a video live inside the terminal, or
2. export the video as a new ASCII-styled video file.

## How to Choose Videos for the Best Output

ASCII art mapping works by transforming pixel brightness (grayscale) values directly into characters. For the best visual results:

1. **High Contrast is Key**: Videos with distinct silhouettes, black-and-white cartoons, dark outlines, or high contrast between foreground and background translate beautifully.
2. **Simple Shapes**: Videos of spinning logos, basic 3D renders, matrix code rain, or simple animations work much better than busy, low-contrast cinematic action scenes.
3. **Low Resolution is Fine**: Since the terminal can only display a few dozen/hundred characters, high-resolution videos (like 4K) won't look any better than 360p or 480p videos, but they will require much more CPU/GPU overhead to process.

---

## Example Commands

### 1. Default Grayscale Mode
Plays the video silently in standard grayscale ASCII representation (fits your terminal window size dynamically):
```bash
python3 vidcii.py example.mp4
```

### 2. High Resolution Dense Mode
Uses the larger, denser ASCII character mapping:
```bash
python3 vidcii.py example.mp4 --charset dense
```

### 3. Colored TrueColor Playback
Renders characters with original pixel RGB values:
```bash
python3 vidcii.py example.mp4 --color
```

### 4. Audio Playback via mpv
Plays audio using `mpv` as the background backend:
```bash
python3 vidcii.py example.mp4 --audio --audio-backend mpv
```

### 5. Audio Playback via ffplay (Video start offset adjustment)
Plays audio via `ffplay` and skips the first 1.5 seconds of video to synchronize:
```bash
python3 vidcii.py example.mp4 --audio --audio-backend ffplay --sync-offset -1.5
```

### 6. Full V2 Setup
Runs the video with both full RGB colors and sound enabled:
```bash
python3 vidcii.py example.mp4 --color --audio
```

### 7. Export to ASCII-styled Video File
Render and export the ASCII art frames directly to a file:
- **Default Resolution (1280x720) Export**:
  ```bash
  python3 vidcii.py example.mp4 --export ascii_output.mp4
  ```
- **HD Preset (1920x1080) Export**:
  ```bash
  python3 vidcii.py example.mp4 --export ascii_output.mp4 --export-preset hd
  ```
- **Colored HD Export**:
  ```bash
  python3 vidcii.py example.mp4 --export ascii_output.mp4 --color --export-preset hd
  ```
- **Custom Spacing & Dense Charset Export**:
  ```bash
  python3 vidcii.py example.mp4 --export ascii_output.mp4 --width 120 --charset dense --font-scale 0.5 --cell-width 10 --cell-height 14
  ```
