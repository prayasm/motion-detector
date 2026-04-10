import argparse
import sys
from pathlib import Path
from typing import List

try:
    import cv2
except ImportError:
    cv2 = None


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".jpe"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="View JPG images from a file or folder."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to a JPG file or a folder containing JPG files. Default: current folder",
    )
    parser.add_argument(
        "--fit-width",
        type=int,
        default=1200,
        help="Resize large images to this width while keeping aspect ratio. Default: 1200",
    )
    return parser


def gather_images(input_path: Path) -> List[Path]:
    if input_path.is_file():
        if input_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"{input_path} is not a supported JPG file.")
        return [input_path]

    if input_path.is_dir():
        images = sorted(
            path
            for path in input_path.iterdir()
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        )
        if images:
            return images
        raise ValueError(f"No JPG images found in {input_path}.")

    raise ValueError(f"Path not found: {input_path}")


def resize_for_display(image, fit_width: int):
    height, width = image.shape[:2]
    if fit_width <= 0 or width <= fit_width:
        return image

    scale = fit_width / width
    new_size = (fit_width, max(1, int(height * scale)))
    return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)


def show_image(window_name: str, image_path: Path, fit_width: int) -> bool:
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"Skipping unreadable image: {image_path}", file=sys.stderr)
        return False

    display_image = resize_for_display(image, fit_width)
    cv2.imshow(window_name, display_image)
    return True


def main() -> int:
    if cv2 is None:
        print(
            "OpenCV is not installed. Run 'python -m pip install -r requirements.txt' first.",
            file=sys.stderr,
        )
        return 1

    args = build_parser().parse_args()

    try:
        images = gather_images(Path(args.path).expanduser().resolve())
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1

    window_name = "JPG Viewer"
    index = 0

    print("Controls: n/right = next, p/left = previous, q/esc = quit")

    while True:
        current_image = images[index]
        shown = show_image(window_name, current_image, args.fit_width)
        if not shown:
            index = (index + 1) % len(images)
            if index == 0:
                cv2.destroyAllWindows()
                return 1
            continue

        print(f"Showing {index + 1}/{len(images)}: {current_image}")
        key = cv2.waitKeyEx(0)

        if key in (ord("q"), 27):
            break
        if key in (ord("n"), 2555904):
            index = (index + 1) % len(images)
            continue
        if key in (ord("p"), 2424832):
            index = (index - 1) % len(images)
            continue

    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
