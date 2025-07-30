import os
import cv2
import sys
import argparse

from pathlib import Path
from typing import Union, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed


def print_progress_bar(current: int, 
                       total: int, 
                       prefix: str = "Process", 
                       bar_width: int = 20) -> None:
    """
    Displays a textual progress bar in the console.

    Parameters
    ----------
    current : int
        Current progress value (e.g., current iteration or frame).
    total : int
        Total number of steps or items to complete.
    prefix : str, optional
        Text prefix displayed before the progress bar (default is "Process").
    bar_width : int, optional
        The total width (in characters) of the progress bar (default is 20).

    Raises
    ------
    TypeError
        If any parameter is of incorrect type.
    ValueError
        If current or total is negative, or total is zero.

    Example
    -------
    >>> print_progress_bar(30, 100)
    Process: [ 30%/100%] ███████--------------- [30/100]
    """
    if not isinstance(current, int) or not isinstance(total, int):
        raise TypeError("current and total must be integers.")
    if not isinstance(prefix, str):
        raise TypeError("prefix must be a string.")
    if not isinstance(bar_width, int):
        raise TypeError("bar_width must be an integer.")
    if current < 0 or total <= 0:
        raise ValueError("current must be >= 0 and total must be > 0.")
    if bar_width <= 0:
        raise ValueError("bar_width must be > 0.")

    percent = int((current / total) * 100)
    bar_filled = int(bar_width * current / total)
    bar = "█" * bar_filled + "-" * (bar_width - bar_filled)
    print(f"\r{prefix}: [{percent:>3}%/100%] {bar} [{current}/{total}]", end='', flush=True)



def determine_worker_count(task_count: Optional[int] = None, reserve_cores: int = 1) -> int:
    """
    Determines the optimal number of worker processes for parallel execution.

    Parameters
    ----------
    task_count : int, optional
        The number of tasks to process. The number of workers will not exceed this value.
    reserve_cores : int, optional
        Number of CPU cores to reserve for the operating system or other processes
        (default is 1).

    Returns
    -------
    int
        The number of worker processes to use.

    Raises
    ------
    TypeError
        If task_count or reserve_cores are of incorrect type.
    ValueError
        If reserve_cores is negative or task_count is not positive (if provided).

    Example
    -------
    >>> determine_worker_count(task_count=10)
    7  # (if os.cpu_count() is 8)
    """
    if task_count is not None and not isinstance(task_count, int):
        raise TypeError("task_count must be an integer or None.")
    if not isinstance(reserve_cores, int):
        raise TypeError("reserve_cores must be an integer.")
    if reserve_cores < 0:
        raise ValueError("reserve_cores must be >= 0.")
    if task_count is not None and task_count <= 0:
        raise ValueError("task_count must be > 0 if provided.")

    total_cores = os.cpu_count() or 1
    usable_cores = max(1, total_cores - reserve_cores)

    if task_count is not None:
        return min(usable_cores, task_count)
    return usable_cores


def extract_frames(video_path: Union[str, Path],
                   output_path: Union[str, Path],
                   step: int = 30,
                   image_prefix: str = "frame",
                   start_sec: Optional[int] = None,
                   end_sec: Optional[int] = None):
    
    """
    Extract frames from a video file and save them as images.

    Parameters:
    ----------
    video_path : str or Path
        Path to the input video file.
    output_path : str or Path
        Directory to save the extracted frames. Will be created if it doesn't exist.
    step : int, default=30
        Save every N-th frame (must be > 0 and <= number of frames in the interval).
    image_prefix : str, default="frame"
        Prefix used for naming saved image files.
    start_sec : int, optional
        Starting time in seconds. Must be >= 0 and <= video duration.
        If None, defaults to the beginning of the video.
    end_sec : int, optional
        Ending time in seconds. Must be >= start_sec and <= video duration.
        If None, defaults to the end of the video.

    Returns:
    -------
    int
        Number of frames saved.

    Raises:
    ------
    ValueError
        If input parameters are invalid or the video file cannot be opened.
    """

    if not isinstance(video_path, (str, Path)):
        raise ValueError("video_path must be a string or Path object.")
    if not isinstance(output_path, (str, Path)):
        raise ValueError("output_path must be a string or Path object.")
    if not isinstance(step, int) or step <= 0:
        raise ValueError("step must be a positive integer.")
    if not isinstance(image_prefix, str):
        raise ValueError("image_prefix must be a string.")

    video_path = Path(video_path)
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")

    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    total_time = total_frames / fps if fps else 0.0
    
    # print(f"  {video_path.name}: fps={fps}, total_frames={total_frames}, total_time={total_time:.2f}")

    if start_sec is None:
        start_sec = 0
    if start_sec < 0 or start_sec > total_time:
        raise ValueError(f"start_sec must be in range [0, {total_time:.2f}] seconds.")

    if end_sec is None or end_sec == 0:
        end_sec = total_time
    if end_sec < start_sec:
        raise ValueError("end_sec must be greater than or equal to start_sec.")
    if end_sec > total_time:
        raise ValueError(f"end_sec must be less than or equal to {total_time:.2f} seconds.")

    start_frame = int(fps * start_sec)
    end_frame = int(fps * end_sec)

    if step > (end_frame - start_frame):
        raise ValueError(f"step must be <= number of frames in range: {end_frame - start_frame}")


    saved = 0
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    current = start_frame

    while current < end_frame:
        ret, frame = cap.read()
        if not ret:
            break

        if (current - start_frame) % step == 0:
            filename = f"{image_prefix}_{current:06d}.jpg"
            filepath = output_path / filename
            cv2.imwrite(str(filepath), frame)
            saved += 1
        
        current += 1

    cap.release()

    return saved


def main():
    parser = argparse.ArgumentParser(description="Parallel video frame extractor.")
    parser.add_argument("--videos", nargs="+", required=True,
                        help="Paths to video files to be processed.")
    parser.add_argument("--output", required=True,
                        help="Directory to save extracted frames.")
    parser.add_argument("--step", type=int, default=10,
                        help="Save every N-th frame (default: 10).")
    parser.add_argument("--prefix", type=str, default="frame",
                        help="Prefix for saved frame filenames.")
    parser.add_argument("--start", type=int, default=0,
                        help="Start time in seconds (default: 0).")
    parser.add_argument("--end", type=int, default=0,
                        help="End time in seconds (0 = until end).")
    parser.add_argument("--reserve", type=int, default=1,
                        help="CPU cores to reserve for OS (default: 1).")
    args = parser.parse_args()

    video_paths = [Path(p) for p in args.videos]
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    for path in video_paths:
        if not path.exists():
            raise FileNotFoundError(f"Video file not found: {path}")
        if not path.is_file():
            raise ValueError(f"Expected file, got directory: {path}")

    max_workers = determine_worker_count(task_count=len(video_paths),
                                         reserve_cores=args.reserve)
    print(f"[INFO] Launching with {max_workers} workers out of {os.cpu_count()} logical cores.")

    total_saved = 0
    completed = 0

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {}

        for i, path in enumerate(video_paths):
            unique_prefix = f"{args.prefix}_{i}"
            future = executor.submit(
                extract_frames,
                path,
                output_dir,
                args.step,
                unique_prefix,
                args.start,
                args.end
            )
            futures[future] = path.name

        print_progress_bar(completed, len(video_paths), prefix="Обработка видео")

        for future in as_completed(futures):
            video_name = futures[future]

            try:
                saved = future.result()
                completed += 1
                total_saved += saved
                print_progress_bar(completed, len(video_paths), prefix="Обработка видео")
                # print(f"\n[✓] {video_name}: {saved} frames saved")
            except Exception as e:
                print(f"[ERROR] Failed to process {video_name}: {e}")

    print(f"\n[INFO] All videos processed. Total frames saved: {total_saved}")


if __name__ == "__main__":
    main()