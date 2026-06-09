#!/usr/bin/env python3
"""
vidcii is a small Python CLI that turns video files into ASCII art.

It can either:
1. play a video live inside the terminal, or
2. export the video as a new ASCII-styled video file.
"""

import argparse
import os
import shutil
import subprocess
import sys
import time

try:
    import cv2
    import numpy as np
except ImportError:
    print("Error: Missing required library 'opencv-python' or 'numpy'.", file=sys.stderr)
    print("Please install the dependencies by running:", file=sys.stderr)
    print("\n    pip install -r requirements.txt\n", file=sys.stderr)
    sys.exit(1)

# ASCII character sets
CHARSETS = {
    'simple': " .:-=+*#%@",
    'dense': " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
}

def validate_width(val):
    """Validate that the width argument is at least 20."""
    try:
        ival = int(val)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid integer value: '{val}'")
    if ival < 20:
        raise argparse.ArgumentTypeError("Width must be at least 20.")
    return ival

def validate_fps(val):
    """Validate that the FPS argument is between 1 and 60."""
    try:
        ival = int(val)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid integer value: '{val}'")
    if ival < 1 or ival > 60:
        raise argparse.ArgumentTypeError("FPS must be between 1 and 60.")
    return ival

def print_video_info(video_path, width, height, fps, frame_count, overridden_fps=None, color_enabled=False, audio_enabled=False, audio_backend=None):
    """Display basic video information before playback starts."""
    print("=" * 50)
    print("  VIDCII: Terminal ASCII Video Player")
    print("=" * 50)
    print(f"File Path:    {os.path.abspath(video_path)}")
    print(f"Resolution:   {width}x{height} pixels")
    
    # Format and display FPS info
    fps_display = f"{fps:.2f}" if isinstance(fps, (int, float)) and fps > 0 else "Unknown/Invalid"
    if overridden_fps:
        print(f"Video FPS:    {fps_display} (Overridden to {overridden_fps})")
    else:
        print(f"Video FPS:    {fps_display}")
        
    # Format and display frame count and duration
    if frame_count and frame_count > 0:
        active_fps = overridden_fps if overridden_fps else (fps if fps > 0 else 15)
        duration_sec = frame_count / active_fps
        mins = int(duration_sec // 60)
        secs = int(duration_sec % 60)
        duration_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"
        print(f"Frame Count:  {frame_count} (~{duration_str})")
    else:
        print("Frame Count:  Not available")
        
    # Display render mode and audio status info
    mode_str = "TrueColor ASCII" if color_enabled else "Grayscale ASCII"
    print(f"Render Mode:  {mode_str}")
    if audio_enabled:
        print(f"Audio:        Enabled (Backend: {audio_backend})")
    else:
        print("Audio:        Disabled (Default)")
    
    print("=" * 50)
    print("Starting playback in 2 seconds... Press Ctrl+C to exit.")
    print("=" * 50)
    time.sleep(2.0)

def frame_to_ascii(frame, target_w, target_h, charset_arr, invert, need_color=False):
    """
    Converts a BGR frame to ASCII characters, optionally returning the resized color frame.
    Returns (ascii_frame, resized_color).
    """
    if need_color:
        resized_color = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(resized_color, cv2.COLOR_BGR2GRAY)
    else:
        resized_color = None
        gray_full = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray_full, (target_w, target_h), interpolation=cv2.INTER_AREA)

    if invert:
        gray = 255 - gray

    num_chars = len(charset_arr)
    indices = (gray.astype(np.float32) * (num_chars - 1) / 255.0).astype(np.int32)
    ascii_frame = charset_arr[indices]
    return ascii_frame, resized_color

def render_ascii_to_terminal(ascii_frame, resized_color, color_enabled):
    """Renders the 2D ASCII frame to the terminal screen."""
    target_h, target_w = ascii_frame.shape
    if color_enabled and resized_color is not None:
        lines = []
        for y in range(target_h):
            row_color = resized_color[y]
            row_char = ascii_frame[y]
            line = "".join(f"\033[38;2;{p[2]};{p[1]};{p[0]}m{c}" for p, c in zip(row_color, row_char))
            lines.append(line)
        frame_str = "\033[H" + "\n".join(lines) + "\033[0m"
    else:
        lines = ["".join(row) for row in ascii_frame]
        frame_str = "\033[H" + "\n".join(lines)

    sys.stdout.write(frame_str)
    sys.stdout.flush()

def render_ascii_to_image(ascii_frame, resized_color, color_enabled, canvas_w, canvas_h, x_padding, y_padding, cell_width, cell_height, font_scale, thickness):
    """Renders the 2D ASCII frame onto a black canvas image of size canvas_h x canvas_w."""
    target_h, target_w = ascii_frame.shape
    
    # Create a black image
    img = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Calculate baseline offset using a reference character 'M'
    ref_size, _ = cv2.getTextSize("M", font, font_scale, thickness)
    ref_h = ref_size[1]
    y_offset = ref_h + (cell_height - ref_h) // 2
    y_offset = max(0, min(cell_height - 1, y_offset))
    
    # Draw character by character to maintain strict monospace alignment
    for y in range(target_h):
        y_pos = y_padding + y * cell_height + y_offset
        for x in range(target_w):
            char = ascii_frame[y, x]
            if char.isspace():
                continue
                
            # Determine character color
            if color_enabled and resized_color is not None:
                b, g, r = resized_color[y, x]
                color = (int(b), int(g), int(r))
            else:
                color = (240, 240, 240) # light-gray/white text
                
            # Center character horizontally in the cell
            char_w = cv2.getTextSize(char, font, font_scale, thickness)[0][0]
            x_offset = (cell_width - char_w) // 2
            x_pos = x_padding + x * cell_width + x_offset
            
            cv2.putText(img, char, (x_pos, y_pos), font, font_scale, color, thickness, lineType=cv2.LINE_AA)
            
    return img

def play_video(args, cap, video_width, video_height, detected_fps, video_frame_count, play_fps, charset_arr, first_frame, audio_enabled):
    """Handles terminal live playback mode."""
    # Display video info before starting playback
    print_video_info(
        args.video_path, video_width, video_height, detected_fps, 
        video_frame_count, args.fps, args.color, audio_enabled, args.audio_backend
    )

    aspect_correction = 0.45
    video_aspect = video_width / video_height

    # Setup terminal display states
    # ANSI escape sequences:
    # \033[?25l - Hide cursor
    # \033[2J   - Clear screen
    sys.stdout.write("\033[?25l\033[2J")
    sys.stdout.flush()

    last_w, last_h = None, None
    frame_duration = 1.0 / play_fps

    # Start audio playback if enabled
    audio_process = None
    if audio_enabled:
        if args.audio_backend == "mpv":
            cmd = ["mpv", "--no-video", "--really-quiet", args.video_path]
        else:  # ffplay
            cmd = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", args.video_path]
            
        try:
            audio_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception:
            pass

    # Handle positive sync offset by sleeping before setting start_time
    if audio_enabled and args.sync_offset > 0:
        time.sleep(args.sync_offset)

    start_time = time.time()
    rendered_frames = 0

    try:
        # Process the first frame that was already read
        frame = first_frame
        
        while True:
            # Get current terminal size
            term_w, term_h = shutil.get_terminal_size()

            # Calculate target render width and height
            if args.width is not None:
                target_w = args.width
                target_h = int(target_w * aspect_correction / video_aspect)
                target_h = max(1, target_h)
            else:
                # Fit within both terminal width and height
                # Try width constraint first
                w1 = term_w
                h1 = int(w1 * aspect_correction / video_aspect)
                
                if h1 <= term_h:
                    target_w = w1
                    target_h = h1
                else:
                    # Height constraint
                    target_h = term_h
                    target_w = int(target_h * video_aspect / aspect_correction)
                    
                target_w = max(1, min(term_w, target_w))
                target_h = max(1, min(term_h, target_h))

            # If the calculated size changes, clear terminal once to clean up ghost lines
            if (target_w, target_h) != (last_w, last_h):
                sys.stdout.write("\033[2J")
                last_w, last_h = target_w, target_h

            # Convert frame to ASCII
            ascii_frame, resized_color = frame_to_ascii(
                frame, target_w, target_h, charset_arr, args.invert, args.color
            )

            # Render ASCII to terminal screen
            render_ascii_to_terminal(ascii_frame, resized_color, args.color)

            # Exact FPS timing implementation
            rendered_frames += 1
            target_time = start_time + rendered_frames * frame_duration
            sleep_time = target_time - time.time()
            
            if sleep_time > 0:
                time.sleep(sleep_time)
            elif sleep_time < -frame_duration:
                # Reset synchronization baseline if lagging behind significantly
                start_time = time.time()
                rendered_frames = 0

            # Read the next frame
            ret, frame = cap.read()
            if not ret or frame is None:
                break

    except KeyboardInterrupt:
        # Exit cleanly on Ctrl+C
        pass
    finally:
        # Release the video capture
        cap.release()
        
        # Stop audio process if running
        if audio_process:
            try:
                audio_process.terminate()
                audio_process.wait()
            except Exception:
                pass

        # ANSI escape sequence:
        # \033[?25h - Show cursor
        # Print a newline to return shell prompt cleanly
        sys.stdout.write("\033[?25h\033[0m\n")
        sys.stdout.flush()

def export_video(args, cap, video_width, video_height, detected_fps, video_frame_count, play_fps, charset_arr, first_frame):
    """Exports the video as an ASCII video file without playing it in the terminal."""
    preset_dims = {
        'small': (854, 480),
        'medium': (1280, 720),
        'hd': (1920, 1080)
    }
    
    preset = args.export_preset
    default_w, default_h = (1280, 720)
    
    if preset:
        pw, ph = preset_dims[preset]
        canvas_w = args.export_width if args.export_width is not None else pw
        canvas_h = args.export_height if args.export_height is not None else ph
    else:
        canvas_w = args.export_width if args.export_width is not None else default_w
        canvas_h = args.export_height if args.export_height is not None else default_h

    # Check validation
    if canvas_w <= 0 or canvas_h <= 0:
        print("Error: Export width and height must be positive integers.", file=sys.stderr)
        cap.release()
        sys.exit(1)
        
    font_scale = args.font_scale
    thickness = args.font_thickness
    cell_w = args.cell_width
    cell_h = args.cell_height
    
    if font_scale <= 0.0 or thickness <= 0 or cell_w <= 0 or cell_h <= 0:
        print("Error: Font scale, thickness, cell width, and cell height must be positive.", file=sys.stderr)
        cap.release()
        sys.exit(1)

    print("=" * 50)
    print("  VIDCII: Export Mode")
    print("=" * 50)
    print(f"Input File:   {os.path.abspath(args.video_path)}")
    print(f"Output File:  {os.path.abspath(args.export)}")
    print(f"Canvas Size:  {canvas_w}x{canvas_h} pixels")
    if preset:
        print(f"Preset:       {preset}")
        
    # Calculate fit within canvas_w x canvas_h preserving original video aspect ratio
    video_aspect = video_width / video_height
    
    if args.width is not None:
        cols = args.width
        # Calculate rows to maintain aspect ratio
        rows = int((cols * cell_w) / (video_aspect * cell_h))
        rows = max(1, rows)
    else:
        if canvas_w / canvas_h > video_aspect:
            # Height is the constraint
            grid_pixel_h = canvas_h
            grid_pixel_w = int(canvas_h * video_aspect)
        else:
            # Width is the constraint
            grid_pixel_w = canvas_w
            grid_pixel_h = int(canvas_w / video_aspect)
            
        cols = int(grid_pixel_w / cell_w)
        rows = int(grid_pixel_h / cell_h)
        cols = max(1, cols)
        rows = max(1, rows)
        
    actual_grid_w = cols * cell_w
    actual_grid_h = rows * cell_h
    
    # If the user-specified grid exceeds the canvas, expand the canvas to fit it
    if actual_grid_w > canvas_w or actual_grid_h > canvas_h:
        canvas_w = max(canvas_w, actual_grid_w)
        canvas_h = max(canvas_h, actual_grid_h)
        
    x_padding = (canvas_w - actual_grid_w) // 2
    y_padding = (canvas_h - actual_grid_h) // 2
    
    print(f"Resolution:   {video_width}x{video_height} -> ASCII {cols}x{rows}")
    print(f"Export Size:  {canvas_w}x{canvas_h} pixels")
    print(f"Target FPS:   {play_fps}")
    print("=" * 50)
    
    # Setup VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(args.export, fourcc, play_fps, (canvas_w, canvas_h))
    if not out.isOpened():
        print(f"Error: OpenCV VideoWriter could not open output file for writing: {args.export}", file=sys.stderr)
        cap.release()
        sys.exit(1)
        
    frame_idx = 0
    frame = first_frame
    
    try:
        while True:
            frame_idx += 1
            if video_frame_count > 0:
                print(f"Exporting frame {frame_idx} / {video_frame_count}...", end="\r")
            else:
                print(f"Exporting frame {frame_idx}...", end="\r")
                
            # Convert frame to ASCII
            ascii_frame, resized_color = frame_to_ascii(
                frame, cols, rows, charset_arr, args.invert, args.color
            )
            
            # Render ASCII to canvas
            img = render_ascii_to_image(
                ascii_frame, resized_color, args.color,
                canvas_w, canvas_h, x_padding, y_padding,
                cell_w, cell_h, font_scale, thickness
            )
            
            # Write frame to video
            out.write(img)
            
            # Read next frame
            ret, frame = cap.read()
            if not ret or frame is None:
                break
                
        print() # print a newline after carriage return progress update
        
    finally:
        out.release()
        cap.release()
        
    # Validate output file
    if not os.path.exists(args.export):
        print(f"Error: Export failed. Output file does not exist: {args.export}", file=sys.stderr)
        sys.exit(1)
        
    file_size = os.path.getsize(args.export)
    if file_size <= 0:
        print(f"Error: Export failed. Output file is empty: {args.export}", file=sys.stderr)
        sys.exit(1)
        
    print("Export complete:")
    print(f"- output: {args.export}")
    print(f"- resolution: {canvas_w}x{canvas_h}")
    print(f"- fps: {play_fps}")
    print(f"- frames: {frame_idx}")

def main():
    parser = argparse.ArgumentParser(
        description="Play videos in the terminal as ASCII art, or export them as ASCII-styled video files."
    )
    parser.add_argument(
        "video_path",
        type=str,
        help="Path to the video file to play or export."
    )
    parser.add_argument(
        "--width",
        type=validate_width,
        default=None,
        help="Target rendering width in characters (minimum 20)."
    )
    parser.add_argument(
        "--fps",
        type=validate_fps,
        default=None,
        help="Target frame rate for playback (1 to 60)."
    )
    parser.add_argument(
        "--charset",
        choices=['simple', 'dense'],
        default='simple',
        help="ASCII character set to use for rendering (default: simple)."
    )
    parser.add_argument(
        "--invert",
        action="store_true",
        help="Invert character brightness mapping."
    )
    parser.add_argument(
        "--color",
        action="store_true",
        help="Render ASCII art in color (TrueColor)."
    )
    parser.add_argument(
        "--audio",
        action="store_true",
        help="Enable audio playback."
    )
    parser.add_argument(
        "--audio-backend",
        choices=["mpv", "ffplay"],
        default="mpv",
        help="Choose which backend to use for audio playback (default: mpv)."
    )
    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="Disable audio playback."
    )
    parser.add_argument(
        "--sync-offset",
        type=float,
        default=0.0,
        help="Optional audio/video sync offset in seconds (positive delays video, negative advances video)."
    )
    parser.add_argument(
        "--export",
        type=str,
        default=None,
        help="Path to the output video file to export. Skips live playback."
    )
    parser.add_argument(
        "--export-width",
        type=int,
        default=None,
        help="Export output video width in pixels."
    )
    parser.add_argument(
        "--export-height",
        type=int,
        default=None,
        help="Export output video height in pixels."
    )
    parser.add_argument(
        "--font-scale",
        type=float,
        default=0.45,
        help="Font scale for ASCII text rendering (default: 0.45)."
    )
    parser.add_argument(
        "--font-thickness",
        type=int,
        default=1,
        help="Font thickness for ASCII text rendering (default: 1)."
    )
    parser.add_argument(
        "--cell-width",
        type=int,
        default=8,
        help="Cell width in pixels for ASCII characters (default: 8)."
    )
    parser.add_argument(
        "--cell-height",
        type=int,
        default=12,
        help="Cell height in pixels for ASCII characters (default: 12)."
    )
    parser.add_argument(
        "--export-preset",
        choices=["small", "medium", "hd"],
        default=None,
        help="Export resolution preset (small: 854x480, medium: 1280x720, hd: 1920x1080)."
    )
    
    args = parser.parse_args()
    
    # 1. Validate file existence
    if not os.path.exists(args.video_path):
        print(f"Error: The video file '{args.video_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
        
    if os.path.isdir(args.video_path):
        print(f"Error: '{args.video_path}' is a directory, not a video file.", file=sys.stderr)
        sys.exit(1)

    # Determine if audio is enabled (only used in live play mode)
    audio_enabled = args.audio and not args.no_audio and not args.export

    if audio_enabled:
        # Validate that the selected backend is available on the system
        if not shutil.which(args.audio_backend):
            print(f"Error: Selected audio backend '{args.audio_backend}' could not be found.", file=sys.stderr)
            print(f"Please install '{args.audio_backend}' or specify another backend with --audio-backend.", file=sys.stderr)
            sys.exit(1)

    # 2. Open the video using OpenCV
    cap = cv2.VideoCapture(args.video_path)
    if not cap.isOpened():
        print(f"Error: OpenCV could not open the video file '{args.video_path}'.", file=sys.stderr)
        sys.exit(1)

    # 3. Retrieve metadata
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    video_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if video_width <= 0 or video_height <= 0:
        print("Error: Invalid video dimensions detected.", file=sys.stderr)
        cap.release()
        sys.exit(1)

    # Respect approximate FPS from video if possible; fall back to 15 if invalid/unrealistic
    if video_fps is None or video_fps <= 0 or np.isnan(video_fps) or video_fps > 100:
        detected_fps = 15.0
    else:
        detected_fps = float(video_fps)

    # Determine play FPS (overridden by command line if specified)
    play_fps = args.fps if args.fps is not None else detected_fps

    # 4. Handle negative sync offset by seeking the video capture forward (only for terminal play mode)
    if audio_enabled and args.sync_offset < 0:
        cap.set(cv2.CAP_PROP_POS_MSEC, abs(args.sync_offset) * 1000.0)

    # Read the first frame before proceeding
    ret, first_frame = cap.read()
    if not ret or first_frame is None:
        print("Error: Could not read any frames from the video file.", file=sys.stderr)
        cap.release()
        sys.exit(1)

    # ASCII charset setup
    charset = CHARSETS[args.charset]
    if args.invert:
        charset = charset[::-1]
    charset_arr = np.array(list(charset))

    # Redirect to either export mode or play mode
    if args.export:
        export_video(args, cap, video_width, video_height, detected_fps, video_frame_count, play_fps, charset_arr, first_frame)
    else:
        play_video(args, cap, video_width, video_height, detected_fps, video_frame_count, play_fps, charset_arr, first_frame, audio_enabled)

if __name__ == '__main__':
    main()
