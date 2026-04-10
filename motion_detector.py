import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import cv2
except ImportError:
    cv2 = None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Detect motion from a webcam feed and optionally save snapshots."
    )
    parser.add_argument(
        "--camera-index",
        type=int,
        default=0,
        help="Webcam index to open. Default: 0",
    )
    parser.add_argument(
        "--min-area",
        type=int,
        default=5000,
        help="Minimum contour area to treat as motion. Default: 5000",
    )
    parser.add_argument(
        "--blur-size",
        type=int,
        default=21,
        help="Odd Gaussian blur kernel size. Default: 21",
    )
    parser.add_argument(
        "--delta-threshold",
        type=int,
        default=25,
        help="Pixel threshold for motion mask. Default: 25",
    )
    parser.add_argument(
        "--save-dir",
        type=Path,
        default=Path("captures"),
        help="Directory for motion snapshots. Default: captures",
    )
    parser.add_argument(
        "--cooldown",
        type=float,
        default=2.0,
        help="Minimum seconds between saved snapshots. Default: 2.0",
    )
    parser.add_argument(
        "--display",
        action="store_true",
        help="Show live webcam, threshold, and delta windows.",
    )
    return parser


def ensure_odd(value: int) -> int:
    if value < 1:
        return 1
    return value if value % 2 == 1 else value + 1


def timestamped_filename() -> str:
    return datetime.now().strftime("motion_%Y%m%d_%H%M%S.jpg")


def main() -> int:
    if cv2 is None:
        print(
            "OpenCV is not installed. Run 'python -m pip install -r requirements.txt' first.",
            file=sys.stderr,
        )
        return 1

    args = build_parser().parse_args()
    blur_size = ensure_odd(args.blur_size)
    args.save_dir.mkdir(parents=True, exist_ok=True)

    capture = cv2.VideoCapture(args.camera_index)
    if not capture.isOpened():
        print(
            f"Could not open camera index {args.camera_index}. "
            "Check that a webcam is connected and not in use.",
            file=sys.stderr,
        )
        return 1

    baseline_frame = None
    last_saved_at = 0.0

    print("Motion detection started. Press Ctrl+C to stop.")
    if args.display:
        print("Press 'q' in the preview window to quit.")

    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                print("Failed to read a frame from the camera.", file=sys.stderr)
                return 1

            resized = cv2.resize(frame, (640, 480))
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (blur_size, blur_size), 0)

            if baseline_frame is None:
                baseline_frame = blurred
                continue

            frame_delta = cv2.absdiff(baseline_frame, blurred)
            _, threshold_frame = cv2.threshold(
                frame_delta, args.delta_threshold, 255, cv2.THRESH_BINARY
            )
            threshold_frame = cv2.dilate(threshold_frame, None, iterations=2)

            contours, _ = cv2.findContours(
                threshold_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            motion_found = False
            for contour in contours:
                if cv2.contourArea(contour) < args.min_area:
                    continue

                motion_found = True
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(resized, (x, y), (x + w, y + h), (0, 255, 0), 2)

            status_text = "Motion detected" if motion_found else "No motion"
            status_color = (0, 0, 255) if motion_found else (0, 255, 0)
            cv2.putText(
                resized,
                status_text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                status_color,
                2,
            )

            current_time = time.time()
            if motion_found and current_time - last_saved_at >= args.cooldown:
                output_path = args.save_dir / timestamped_filename()
                cv2.imwrite(str(output_path), resized)
                last_saved_at = current_time
                print(f"[{datetime.now().isoformat(timespec='seconds')}] Saved {output_path}")

            # Slowly adapt the baseline so lighting changes do not trigger forever.
            baseline_frame = cv2.addWeighted(baseline_frame, 0.9, blurred, 0.1, 0)

            if args.display:
                cv2.imshow("Motion Detector", resized)
                cv2.imshow("Frame Delta", frame_delta)
                cv2.imshow("Threshold", threshold_frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    except KeyboardInterrupt:
        pass
    finally:
        capture.release()
        cv2.destroyAllWindows()

    print("Motion detection stopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
