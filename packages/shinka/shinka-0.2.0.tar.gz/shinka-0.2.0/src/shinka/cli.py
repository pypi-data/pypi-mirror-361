import logging
import multiprocessing
from pathlib import Path
from typing import List, Never

import typer
from rich.console import Console
from rich.logging import RichHandler

from .batch import BatchUpscaler
from .core import upscale

try:
    from . import __version__
except ImportError:
    __version__ = "0.0.0-dev"


def validate_scale(value: int) -> int:
    if value < 1:
        raise typer.BadParameter("must be >= 1")
    return value


SUPPORTED_BOUNDARIES = ["reflect", "constant", "nearest", "mirror", "wrap"]


def validate_boundary(value: str) -> str:
    cleaned_value = value.strip().lower()
    if cleaned_value not in [b.lower() for b in SUPPORTED_BOUNDARIES]:
        raise typer.BadParameter(f"Unsupported boundary mode. Choose from: {SUPPORTED_BOUNDARIES}")
    return cleaned_value


def version_callback(value: bool) -> None:
    if value:
        console.print(f"shinka v{__version__}")
        raise typer.Exit()


app = typer.Typer(
    help="Image upscaler using a 5-tap kernel (HALO tap). Supports single image and batch modes.",
    add_completion=False,
    no_args_is_help=True,
)


@app.callback()
def main_callback(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    )
) -> None:
    pass


console = Console()
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    handlers=[RichHandler(console=console, show_time=False, rich_tracebacks=True)],
)
logger = logging.getLogger("upscaler")


def rich_exit(msg: str, error: bool = True) -> Never:
    if error:
        console.print(f"[bold red]{msg}")
        raise typer.Exit(code=1)
    else:
        console.print(f"[bold green]{msg}")
        raise typer.Exit(code=0)


@app.command()
def single(
    src: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, help="Input image file"),  # noqa: B008
    scale: int = typer.Option(..., "--scale", "-s", callback=validate_scale, help="Integer scale factor"),
    dst: Path = typer.Option(None, "--output", "-o", help="Output file path"),  # noqa: B008
    boundary: str = typer.Option(
        "reflect",
        "--boundary",
        "-b",
        case_sensitive=False,
        help="Convolution boundary mode.",
        show_choices=True,
        rich_help_panel="Advanced",
        autocompletion=lambda: SUPPORTED_BOUNDARIES,
        callback=validate_boundary,
    ),
) -> None:
    """Upscale a single image."""
    try:
        out = upscale(src, scale=scale, save_path=dst, boundary=boundary)
        rich_exit(f"Saved to {out}", error=False)
    except FileExistsError as e:
        rich_exit(str(e), error=False)
    except Exception as e:
        rich_exit(f"Error: {e}")


@app.command()
def batch(
    src_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Directory of images"),  # noqa: B008
    scale: int = typer.Option(..., "--scale", "-s", callback=validate_scale, help="Integer scale factor"),
    out_dir: Path = typer.Option(None, "--output", "-o", help="Output directory"),  # noqa: B008
    pattern: List[str] = typer.Option(  # noqa: B008
        ["*.png", "*.jpg", "*.jpeg"],
        "--pattern",
        "-p",
        help="Glob patterns for input files",
    ),
    boundary: str = typer.Option(
        "reflect",
        "--boundary",
        "-b",
        case_sensitive=False,
        help="Convolution boundary mode.",
        show_choices=True,
        rich_help_panel="Advanced",
        autocompletion=lambda: SUPPORTED_BOUNDARIES,
        callback=validate_boundary,
    ),
    workers: int = typer.Option(
        0,
        "--workers",
        "-w",
        help="Number of parallel processes (0 = CPU-1)",
        min=0,
    ),
) -> None:
    """Recursively upscale all matching images in a directory."""
    n_cpu = (multiprocessing.cpu_count() or 2) - 1
    _ = workers or max(1, n_cpu)
    ups = BatchUpscaler()
    try:
        ups.upscale_dir(
            input_dir=src_dir,
            scale=scale,
            output_dir=out_dir,
            pattern=pattern,
            boundary=boundary,
            verbose=True
        )
    except Exception as e:
        rich_exit(f"Batch error: {e}")


if __name__ == "__main__":
    app() 