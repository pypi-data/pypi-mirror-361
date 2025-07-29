import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional, Sequence, Union

from .core import upscale

try:
    from rich.console import Console
    from rich.progress import (
        BarColumn,
        Progress,
        TextColumn,
        TimeElapsedColumn,
        TimeRemainingColumn,
    )
    console = Console()
except ImportError:
    Progress = None
    console = None

def split_into_batches(files: List[Path], n_batches: int) -> List[List[Path]]:
    k, m = divmod(len(files), n_batches)
    return [files[i*k + min(i, m):(i+1)*k + min(i+1, m)] for i in range(n_batches)]

def get_output_path(f: Path, output_dir: Optional[Path]) -> Optional[Path]:
    return Path(output_dir) / Path(f).name if output_dir is not None else None

def print_summary(n: int, output_dir: Optional[Path], input_dir: Path) -> None:
    if output_dir is not None:
        msg = f"Upscaled {n} images to directory: {output_dir}"
    else:
        msg = f"Upscaled {n} images next to originals in: {input_dir}"
    if console:
        console.print(f"[bold green]{msg}")
    else:
        print(msg)

def batch_worker(
    batch: List[Path], scale: int, output_dir: Optional[Path], boundary: str, task_id: Optional[int] = None
) -> List[str]:
    results = []
    for f in batch:
        out_path = get_output_path(f, output_dir)
        results.append(upscale(f, scale, save_path=out_path, boundary=boundary, verbose=False))
    return results

class BatchUpscaler:
    def __init__(self) -> None:
        pass

    def upscale_dir(
        self,
        input_dir: Union[str, Path],
        scale: int,
        output_dir: Optional[Union[str, Path]] = None,
        pattern: Sequence[str] = ("*.png", "*.jpg", "*.jpeg"),
        boundary: str = 'reflect',
        verbose: bool = False
    ) -> None:
        """
        Upscale all images in a directory by a given scale, using all CPU cores minus one.
        Args:
            input_dir: Directory containing images.
            scale: Integer upscaling factor.
            output_dir: Where to save upscaled images. If None, saves next to input.
            pattern: File patterns to match (tuple of globs).
            boundary: Convolution boundary mode.
            verbose: Print summary info at the end.
        """
        if console:
            console.print(f"[yellow]DEBUG: Using boundary mode: {boundary}")
        else:
            print(f"DEBUG: Using boundary mode: {boundary}")
        input_dir = Path(input_dir)
        if output_dir is not None:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        files = []
        for pat in pattern:
            files.extend(sorted(input_dir.glob(pat)))
        if not files:
            if console:
                console.print(f"[red]No images found in {input_dir} matching {pattern}")
            else:
                print(f"No images found in {input_dir} matching {pattern}")
            return
        n_workers = max(1, (os.cpu_count() or 2) - 1)
        batches = split_into_batches(files, n_workers)
        all_results: List[str] = []
        if console and Progress:
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                "[",
                TextColumn("{task.completed}/{task.total}"),
                "]",
                TimeElapsedColumn(),
                TimeRemainingColumn(),
                console=console,
                transient=True
            ) as progress:
                batch_tasks = []
                for i, batch_list in enumerate(batches):
                    desc = f"Batch {i+1}/{n_workers}"
                    task_id = progress.add_task(desc, total=len(batch_list))
                    batch_tasks.append((task_id, batch_list))
                with ProcessPoolExecutor(max_workers=n_workers) as executor:
                    futures = [executor.submit(batch_worker, batch_list, scale, output_dir, boundary, task_id)
                               for (task_id, batch_list) in batch_tasks]
                    for (future, (task_id, batch_item)) in zip(as_completed(futures), batch_tasks, strict=False):
                        progress.update(task_id, completed=len(batch_item))
                        all_results.extend(future.result())
        else:
            # Fallback: sequential
            for f in files:
                out_path = get_output_path(f, output_dir)
                all_results.append(upscale(f, scale, save_path=out_path, boundary=boundary, verbose=False))
        # Print summary at the end
        if verbose:
            print_summary(len(files), output_dir, input_dir)

batch = BatchUpscaler 