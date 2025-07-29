"""syrenka.generate"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Union

MMDC_DEFAULT = "mmdc"
MMDC_EXE = os.environ.get("SYRENKA_MMDC", MMDC_DEFAULT)
MMDC_SUPPORT = False

p = shutil.which(MMDC_EXE)
if p:
    MMDC_EXE = str(Path(p).resolve())
    MMDC_SUPPORT = True

if not MMDC_SUPPORT:
    print(
        "For local mermaid diagram generation there needs to be mermaid-cli installed\n"
        f"For different executable name set SYRENKA_MMDC env variable, default is '{MMDC_DEFAULT}'"
        "see https://github.com/mermaid-js/mermaid-cli for reference",
        file=sys.stderr,
    )


def generate_diagram_image(
    source: Union[str, Path],
    output_file: Path,
    overwrite: bool = False,
    # mmdc specific args
    theme: Union[str, None] = None,
    width: Union[int, None] = None,
    height: Union[int, None] = None,
    background_color: Union[str, None] = None,
    config_file: Union[str, Path, None] = None,
    css_file: Union[str, Path, None] = None,
):
    print("`generate_diagram_image` is deprecated, use `render_mermaid` function", file=sys.stderr)
    return render_mermaid(source, output_file, overwrite, theme, width, height, background_color, config_file, css_file)


def render_mermaid(
    source: Union[str, Path],
    output_file: Path,
    overwrite: bool = False,
    # mmdc specific args
    theme: Union[str, None] = None,
    width: Union[int, None] = None,
    height: Union[int, None] = None,
    background_color: Union[str, None] = None,
    config_file: Union[str, Path, None] = None,
    css_file: Union[str, Path, None] = None,
):
    """generates diagram image using mermaid-cli - mmdc"""
    if not MMDC_SUPPORT:
        print("For mermaid diagram generation install mmdc, check stderr", file=sys.stderr)
        return

    of = output_file.resolve()
    if of.exists() and not overwrite:
        raise FileExistsError(f"Output file: {of}, already exists and overwrite is {overwrite}")

    if isinstance(source, Path):
        input_str = None
        input_arg = str(source)
    elif isinstance(source, str):
        input_str = source
        input_arg = "-"
    else:
        raise ValueError(f"unexpected input type: {type(source)} - expected Path or str")

    args = [MMDC_EXE, "-i", input_arg, "-o", str(of)]

    if theme:
        args.extend(["-t", theme])
    if background_color:
        args.extend(["-b", background_color])
    if width:
        args.extend(["-w", str(width)])
    if height:
        args.extend(["-H", str(height)])
    if config_file:
        args.extend(["-c", str(config_file)])
    if css_file:
        args.extend(["-C", str(css_file)])

    subprocess.run(args, input=input_str, text=True, capture_output=True, check=False)
