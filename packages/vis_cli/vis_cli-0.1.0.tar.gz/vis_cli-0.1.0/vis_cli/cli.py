#!/usr/bin/env python3

r"""
vis visualizes fuzzy tabular data, no script required.

Notes
-----
- By default, vis indexes by regex-matching floats in each row, but use --static to index by column number instead.

Examples
--------
# Histogram - uniform distribution
awk 'BEGIN { for (i = 0; i < 1000; i++) print rand() * 100 }' | vis hist --kde

# Scatter plot - simulated data
echo -e '1 2\n1.5 3\n2 1\n3 1.5\n2 2' | vis scatter --trend

# Line plot - sin(t)
seq 0 0.1 10 | awk '{print $1, sin($1)}' | vis line --xlab "Time" --ylab "sin(t)"

# Histogram - CPU utilization for all nodes in a Kubernetes cluster
kubectl top nodes | vis hist --static --col 2 --bins 10 --xmax 100 --xlab 'CPU util' --kde

# Scatter plot - CPU:memory shapes for all pods in a Kubernetes cluster
kubectl resource-capacity --pods | grep -v '\*.*\*' | vis scatter --static --cols 4 6 --xlab "CPU limits" --ylab "Memory limits" --trend

# Clean - clean and pass to e.g. visidata
python -c "import random as r; [print(r.randint(0,100), r.randint(0,100)) for _ in range(100)]" | vis clean --dim 2 --head 'x,y' --osep , | visidata

Related
-------
- bashplotlib - https://github.com/glamp/bashplotlib
- visidata - https://github.com/saulpw/visidata
"""

import os
import re
import sys
from dataclasses import dataclass
from typing import Optional

import click
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.stats import linregress

NUMERIC_REGEX = re.compile(r"[-+]?(?:\d*\.\d+|\d+)")


@click.group(context_settings=dict(help_option_names=["-h", "--help"], max_content_width=120))
def cli():
    """A fuzzy tabular data visualization tool."""
    pass


@cli.command(name="hist")
@click.option("--bins", "n_bins", type=int, default=0, show_default=True, help="Number of bins for the histogram.")
@click.option("--file", "-f", default="-", show_default=True, help="Path to the input file. Defaults to stdin.")
@click.option("--save", is_flag=True, help="Save the plot to file instead of displaying it.")
@click.option("--justsave", is_flag=True, help="Save the plot to file without displaying it.")
@click.option("--output", "-o", help="Output filename for the plot.")
@click.option("--xlab", default="Value", show_default=True, help="Label for the x-axis.")
@click.option("--title", help="Title for the plot.")
@click.option("--col", type=int, default=0, show_default=True, help="Column index to plot.")
@click.option("--static", is_flag=True, help="Use cols to index into columns instead of list of floats.")
@click.option("--sep", type=str, default=None, help="Separator for the input columns. Implies --static.")
@click.option("--xmin", type=float, default=None, help="Filter x-axis values below.")
@click.option("--xmax", type=float, default=None, help="Filter x-axis values above.")
@click.option("--barcolor", type=str, default="skyblue", help="Color for the histogram bars.")
@click.option("--baredge", type=str, default="black", help="Edge color for the histogram bars.")
@click.option("--baralpha", type=float, default=0.75, help="Alpha value for the histogram bars.")
@click.option("--kde", is_flag=True, help="Add a kernel density estimate (KDE) to the histogram.")
@click.option("--strict", is_flag=True, help="Fail on parse errors instead of skipping them.")
@click.option("--force", is_flag=True, help="Overwrite the output file if it exists.")
@click.option("--verbose", is_flag=True, help="Print verbose output.")
def hist_cmd(
    n_bins: int,
    file: str,
    save: bool,
    justsave: bool,
    output: str,
    xlab: str,
    title: str,
    col: int,
    static: bool,
    sep: Optional[str],
    xmin: Optional[float],
    xmax: Optional[float],
    barcolor: str,
    baredge: str,
    baralpha: float,
    kde: bool,
    strict: bool,
    force: bool,
    verbose: bool,
):
    """Create a histogram from numerical data."""
    rows = read_data(file)
    x = get_1d_values(rows, col, static=static, sep=sep, xmin=xmin or float("-inf"), xmax=xmax or float("inf"), strict=strict, sort=kde, verbose=verbose)

    plt.close()  # HACK: close the implicit figure
    plt.figure(figsize=(10, 6), dpi=100)
    plt.locator_params(axis="both", integer=True, tight=True)
    binrange = None
    if xmin is not None or xmax is not None:
        binrange = (xmin or x.min(), xmax or x.max())
        plt.xlim(*binrange)
    sns.histplot(x, bins=n_bins or "auto", binrange=binrange, color=barcolor, edgecolor=baredge, alpha=baralpha, kde=kde, label=f"{xlab} (n = {len(x)})")
    plt.title(title or "Histogram of Input Data", fontsize=16, fontweight="bold")
    plt.legend(fontsize=12)
    plt.xlabel(xlab, fontsize=14)
    plt.ylabel("Frequency", fontsize=14)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.xticks(fontsize=12)
    plt.tight_layout()

    do_save = save or justsave
    do_show = not justsave
    if do_save:
        save_plot(output or title_to_filename(title, "hist"), force)
    if do_show:
        plt.show()


@cli.command(name="line")
@click.option("--file", "-f", default="-", show_default=True, help="Path to the input file. Defaults to stdin.")
@click.option("--save", is_flag=True, help="Save the plot to file instead of displaying it.")
@click.option("--justsave", is_flag=True, help="Save the plot to file without displaying it.")
@click.option("--output", "-o", help="Output filename for the plot.")
@click.option("--xlab", default="Column 0", show_default=True, help="Label for the x-axis.")
@click.option("--ylab", default="Column 1", show_default=True, help="Label for the y-axis.")
@click.option("--title", help="Title for the plot.")
@click.option("--cols", type=int, nargs=2, default=(0, 1), show_default=True, help="Column indices to plot.")
@click.option("--static", is_flag=True, help="Use cols to index into columns instead of list of floats.")
@click.option("--sep", type=str, default=None, help="Separator for the input columns. Implies --static.")
@click.option("--xmin", type=float, default=None, help="Filter x-axis values below.")
@click.option("--xmax", type=float, default=None, help="Filter x-axis values above.")
@click.option("--ymin", type=float, default=None, help="Filter y-axis values below.")
@click.option("--ymax", type=float, default=None, help="Filter y-axis values above.")
@click.option("--linecolor", type=str, default="skyblue", help="Set the color for the points.")
@click.option("--strict", is_flag=True, help="Fail on parse errors instead of skipping them.")
@click.option("--force", is_flag=True, help="Overwrite the output file if it exists.")
@click.option("--verbose", is_flag=True, help="Print verbose output.")
def line_cmd(
    file: str,
    save: str,
    justsave: bool,
    output: str,
    xlab: str,
    ylab: str,
    title: str,
    cols: tuple[int, int],
    static: bool,
    sep: Optional[str],
    xmin: Optional[float],
    xmax: Optional[float],
    ymin: Optional[float],
    ymax: Optional[float],
    linecolor: str,
    strict: bool,
    force: bool,
    verbose: bool,
):
    """Create a line plot from tabular data."""
    rows = read_data(file)
    x, y = get_2d_values(
        rows,
        cols,
        static=static,
        sep=sep,
        xmin=xmin or float("-inf"),
        xmax=xmax or float("inf"),
        ymin=ymin or float("-inf"),
        ymax=ymax or float("inf"),
        strict=strict,
        sort=True,
        verbose=verbose,
    )

    plt.close()  # HACK: close the implicit figure
    plt.figure(figsize=(10, 6), dpi=100)
    plt.locator_params(axis="both", integer=True, tight=True)
    if xmin is not None or xmax is not None:
        plt.xlim(xmin or x.min(), xmax or x.max())
    if ymin is not None or ymax is not None:
        plt.ylim(ymin or y.min(), ymax or y.max())
    sns.lineplot(x=x, y=y, color=linecolor, label=f"{ylab} (n = {len(x)})")
    plt.title(title or "Line Plot of Input Data", fontsize=16, fontweight="bold")
    plt.legend(fontsize=12)
    plt.xlabel(xlab, fontsize=14)
    plt.ylabel(ylab, fontsize=14)
    plt.grid(linestyle="--", alpha=0.7)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout()

    do_save = save or justsave
    do_show = not justsave
    if do_save:
        save_plot(output or title_to_filename(title, "line"), force)
    if do_show:
        plt.show()


@cli.command(name="scatter")
@click.option("--file", "-f", default="-", show_default=True, help="Path to the input file. Defaults to stdin.")
@click.option("--save", is_flag=True, help="Save the plot to file instead of displaying it.")
@click.option("--justsave", is_flag=True, help="Save the plot to file without displaying it.")
@click.option("--output", "-o", help="Output filename for the plot.")
@click.option("--xlab", default="Column 0", show_default=True, help="Label for the x-axis.")
@click.option("--ylab", default="Column 1", show_default=True, help="Label for the y-axis.")
@click.option("--title", help="Title for the plot.")
@click.option("--cols", type=int, nargs=2, default=(0, 1), show_default=True, help="Column indices to plot.")
@click.option("--static", is_flag=True, help="Use cols to index into columns instead of list of floats.")
@click.option("--sep", type=str, default=None, help="Separator for the input columns. Implies --static.")
@click.option("--xmin", type=float, default=None, help="Filter x-axis values below.")
@click.option("--xmax", type=float, default=None, help="Filter x-axis values above.")
@click.option("--ymin", type=float, default=None, help="Filter y-axis values below.")
@click.option("--ymax", type=float, default=None, help="Filter y-axis values above.")
@click.option("--pointsize", type=float, default=0, help="Set a static point size for the scatter plot.")
@click.option("--pointalpha", type=float, default=0, help="Set a static alpha value for the points.")
@click.option("--pointcolor", type=str, default="skyblue", help="Set the color for the points.")
@click.option("--pointedge", type=str, default="", help="Set the edge color for the points.")
@click.option("--trend", is_flag=True, help="Add a linear regression trendline to the plot.")
@click.option("--trendcolor", type=str, default="skyblue", help="Set the color for the trendline.")
@click.option("--trendstyle", type=str, default="--", help="Set the style for the trendline.")
@click.option("--strict", is_flag=True, help="Fail on parse errors instead of skipping them.")
@click.option("--force", is_flag=True, help="Overwrite the output file if it exists.")
@click.option("--verbose", is_flag=True, help="Print verbose output.")
def scatter_cmd(
    file: str,
    save: str,
    justsave: bool,
    output: str,
    xlab: str,
    ylab: str,
    title: str,
    cols: tuple[int, int],
    static: bool,
    sep: Optional[str],
    xmin: Optional[float],
    xmax: Optional[float],
    ymin: Optional[float],
    ymax: Optional[float],
    pointsize: float,
    pointalpha: float,
    pointcolor: str,
    pointedge: str,
    trend: bool,
    trendcolor: str,
    trendstyle: str,
    strict: bool,
    force: bool,
    verbose: bool,
):
    """Create a scatter plot from tabular data."""
    rows = read_data(file)
    x, y = get_2d_values(
        rows,
        cols,
        static=static,
        sep=sep,
        xmin=xmin or float("-inf"),
        xmax=xmax or float("inf"),
        ymin=ymin or float("-inf"),
        ymax=ymax or float("inf"),
        strict=strict,
        sort=trend,
        verbose=verbose,
    )
    n = len(x)

    pointalpha = pointalpha or point_alpha(n)
    pointsize = pointsize or point_size(n)
    pointedge = pointedge or point_edge(n)

    plt.close()  # HACK: close the implicit figure
    plt.figure(figsize=(10, 6), dpi=100)
    plt.locator_params(axis="both", integer=True, tight=True)
    if xmin is not None or xmax is not None:
        plt.xlim(xmin or x.min(), xmax or x.max())
    if ymin is not None or ymax is not None:
        plt.ylim(ymin or y.min(), ymax or y.max())
    plt.scatter(x, y, color=pointcolor, edgecolor=pointedge, alpha=pointalpha, s=pointsize, label=f"{ylab} × {xlab} (n = {len(x)})")
    if trend:
        m, b, rvalue, _, _ = linregress(x, y)
        plt.plot(x, m * x + b, color=trendcolor, linestyle=trendstyle, label=f"Trendline (m = {m:.3f}, b = {b:.3f}, ρ = {rvalue:.3f}, R² = {rvalue ** 2:.3f})")
    plt.title(title or "Scatter Plot of Input Data", fontsize=16, fontweight="bold")
    plt.legend(fontsize=12)
    plt.xlabel(xlab, fontsize=14)
    plt.ylabel(ylab, fontsize=14)
    plt.grid(linestyle="--", alpha=0.7)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout()

    do_save = save or justsave
    do_show = not justsave
    if do_save:
        save_plot(output or title_to_filename(title, "scatter"), force)
    if do_show:
        plt.show()


def parse_cols(_: click.Context, __: click.Parameter, value: Optional[str]) -> Optional[tuple[int, ...]]:
    """Parse a comma-separated list of column indices into a tuple of integers."""
    if value is None:
        return None
    try:
        return tuple(int(c) for c in value.split(","))
    except ValueError:
        raise click.BadParameter(f"invalid column indices: '{value}'")


@cli.command(name="clean")
@click.option("--file", "-f", default="-", show_default=True, help="Path to the input file. Defaults to stdin.")
@click.option("--dim", type=int, default=None, show_default=True, help="How many columns to output.")
@click.option("--cols", type=str, default=None, callback=parse_cols, help="Column indices to clean, comma-separated.")
@click.option("--static", is_flag=True, help="Use cols to index into columns instead of list of floats.")
@click.option("--sep", type=str, default=None, help="Separator for the input columns. Implies --static.")
@click.option("--head", type=str, default=None, help="Header row to prepend to the output.")
@click.option("--osep", type=str, default=" ", help="Separator for the output columns.")
@click.option("--strict", is_flag=True, help="Fail on parse errors instead of skipping them.")
@click.option("--sort", is_flag=True, help="Sort the output.")
@click.option("--verbose", is_flag=True, help="Print verbose output.")
def clean_cmd(
    file: str,
    dim: Optional[int],
    cols: Optional[str],
    static: bool,
    sep: Optional[str],
    head: Optional[str],
    osep: str,
    strict: bool = False,
    sort: bool = False,
    verbose: bool = False,
):
    """Clean the data from a file or stdin and print it to stdout."""
    if dim and cols:
        raise click.ClickException("cannot specify both --dim and --cols")
    if dim is not None:
        cols = tuple(range(dim))
    if cols is None:
        cols = (0,)

    rows = read_data(file)
    vals = get_nd_values(
        rows,
        cols,
        static=static,
        sep=sep,
        strict=strict,
        sort=sort,
        verbose=verbose,
    )
    if head:
        click.echo(head)
    for val in zip(*vals):
        click.echo(osep.join(str(v) for v in val))


def get_1d_values(
    rows: list[str],
    col: int,
    *,
    static: bool,
    sep: Optional[str],
    xmin: float,
    xmax: float,
    strict: bool,
    sort: bool,
    verbose: bool,
) -> np.ndarray:
    """Extract 1D values from a list of strings."""
    vals = get_nd_values(
        rows,
        (col,),
        static=static,
        sep=sep,
        bounds=(Bound(xmin, xmax),),
        strict=strict,
        sort=sort,
        verbose=verbose,
    )
    if len(vals) != 1:
        raise click.ClickException(f"expected 1D data, got {len(vals)}D")
    return vals[0]


def get_2d_values(
    rows: list[str],
    cols: tuple[int, int],
    *,
    static: bool,
    sep: Optional[str],
    xmin: float,
    xmax: float,
    ymin: float,
    ymax: float,
    strict: bool,
    sort: bool,
    verbose: bool,
) -> tuple[np.ndarray, np.ndarray]:
    """Extract 2D values from a list of strings."""
    vals = get_nd_values(
        rows,
        cols,
        static=static,
        sep=sep,
        bounds=(Bound(xmin, xmax), Bound(ymin, ymax)),
        strict=strict,
        sort=sort,
        verbose=verbose,
    )
    if len(vals) != 2:
        raise click.ClickException(f"expected 2D data, got {len(vals)}D")
    return vals[0], vals[1]


@dataclass
class Bound:
    min: float
    max: float


def get_nd_values(
    rows: list[str],
    cols: tuple[int, ...],
    *,
    static: bool,
    sep: Optional[str],
    bounds: Optional[tuple[Bound, ...]] = None,
    strict: bool,
    sort: bool,
    verbose: bool,
) -> tuple[np.ndarray, ...]:
    """Extract N-D values from a list of strings."""
    if bounds is None:
        bounds = (Bound(float("-inf"), float("inf")),) * len(cols)
    if sep is not None:
        static = True

    vals: list[tuple[float, ...]] = []
    for i, row in enumerate(rows):
        try:
            val = parse_floats(row, cols, static, sep)
            if all(b.min < v < b.max for b, v in zip(bounds, val)):
                vals.append(val)
        except IndexError:
            msg = f"index error for columns {cols} in row {i}: '{row}'"
            if strict:
                raise click.ClickException(msg)
            if verbose:
                click.echo(f"WARN: {msg}", err=True)
        except ValueError as e:
            msg = f"invalid row {i} ignored '{row}': {e}"
            if strict:
                raise click.ClickException(msg)
            if verbose:
                click.echo(f"WARN: {msg}", err=True)
    if not vals:
        raise click.ClickException("no valid numeric data provided")

    if sort:
        vals.sort()

    return tuple(np.array(col) for col in zip(*vals))


def point_alpha(n: int) -> float:
    """
    Calculate the points' alpha value based on the number of points.

    Function is an inverse power function fitting the following points:
    - (1, 1)
    - (10, 0.7)
    - (100k, 0.17)
    """
    raw = 1 / (n**0.15)
    return max(0.2, min(1, raw))


def point_size(n: int) -> float:
    """
    Calculate the points' size based on the number of points.

    Function is a modified inverse power function fitting the following points:
    - (10, 100)
    - (100, 40)
    - (100k, 1)
    """
    raw = 252.83 / (n**0.402)
    return max(1, min(100, raw))


def point_edge(n: int) -> str:
    """Calculate the points' edge color based on the number of points."""
    return "black" if n <= 1_000 else "none"


def parse_floats(row: str, cols: tuple[int, ...], static: bool, sep: str) -> tuple[float, ...]:
    """Parse a row of strings as floats."""
    if static:
        columns = tuple(v for v in row.split(sep) if v.strip())
        return tuple(parse_float(columns[col]) for col in cols)
    else:
        columns = NUMERIC_REGEX.findall(row)
        return tuple(float(columns[col]) for col in cols)


def parse_float(val: str) -> float:
    """Parse a string as a float."""
    return float(longest_matching_substr(val, NUMERIC_REGEX))


def longest_matching_substr(s: str, allowed: re.Pattern) -> str:
    """Find the longest substring of s that consists only of characters matching the regex allowed."""
    return max(allowed.findall(s), key=len, default="")


def title_to_filename(title: str, backup_title: str) -> str:
    """Convert a title to a valid filename."""
    title = title or backup_title
    return f"{''.join(c.lower() if c.isalnum() else '_' for c in title)}.png"


def save_plot(path: str, force: bool):
    """Save the current plot to a file."""
    path = path if path.endswith(".png") else f"{path}.png"  # matplotlib adds .png if not present
    if os.path.exists(path) and not force:
        raise click.ClickException(f"'{path}' already exists, use --force to overwrite")
    plt.savefig(path)
    click.echo(f"Saved plot to: {os.path.realpath(path)}")


def read_data(file: str) -> list[str]:
    """Reads data from a file or stdin."""
    if file and file != "-":
        if not os.path.exists(file):
            raise click.ClickException(f"file not found: {file}")
        try:
            with open(file, "r") as f:
                return [x for l in f.read().strip().splitlines() if (x := strip_ansi(l).strip())]
        except Exception as e:
            raise click.ClickException(f"unable to read file: {file}: {e}")
    else:
        return [x for l in sys.stdin.read().strip().splitlines() if (x := strip_ansi(l).strip())]


ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def strip_ansi(txt: str) -> str:
    """
    Strip ANSI escape sequences from text.

    REF: https://stackoverflow.com/questions/14693701
    """
    return ANSI_ESCAPE.sub("", txt)


if __name__ == "__main__":
    cli()
