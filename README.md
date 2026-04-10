# Motion Detection Program

This project uses OpenCV to watch a webcam feed, detect motion, draw bounding boxes around moving regions, and save snapshots when movement is detected.

## Requirements

- Python 3.10 or newer
- A connected webcam

## Install

```powershell
python -m pip install -r requirements.txt
```

## Run

```powershell
python motion_detector.py --display
```

Snapshots are saved into the `captures` folder by default.

## Useful options

```powershell
python motion_detector.py --display --min-area 3000 --cooldown 1.5
```

- `--camera-index`: Select a different webcam.
- `--min-area`: Lower this if smaller movements should count as motion.
- `--blur-size`: Increase this if the feed is noisy.
- `--delta-threshold`: Lower this for more sensitive detection.
- `--save-dir`: Change where snapshots are stored.
- `--cooldown`: Time between saved motion snapshots.

## Controls

- Press `q` in the preview window to quit when `--display` is enabled.
- Press `Ctrl+C` to stop from the terminal.

## JPG Viewer

Open a JPG file:

```powershell
python jpg_viewer.py path\to\image.jpg
```

Open all JPG files in a folder:

```powershell
python jpg_viewer.py path\to\folder
```

Controls:

- `n` or Right Arrow: next image
- `p` or Left Arrow: previous image
- `q` or `Esc`: quit
