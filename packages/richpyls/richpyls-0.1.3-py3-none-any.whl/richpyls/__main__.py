#!/usr/bin/env python3
import grp
import pwd
import stat
import time
from os import stat_result
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text

from . import __version__

# Initialize Rich console
console = Console()
error_console = Console(stderr=True)


def get_file_style_and_icon(path: Path) -> tuple[str, str]:
    """Get Rich style and icon for a file based on its type and extension."""
    # File type mappings
    file_types = {
        # Python files
        (".py", ".pyx", ".pyi"): ("green", "🐍"),
        # Configuration files
        (".toml", ".json", ".yaml", ".yml", ".ini", ".cfg", ".conf"): ("yellow", "⚙️"),
        # Documentation files
        (".md", ".rst", ".txt", ".doc", ".docx", ".pdf"): ("magenta", "📄"),
        # Archive files
        (".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar"): ("red", "📦"),
        # Image files
        (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".ico"): (
            "bright_magenta",
            "🖼️",
        ),
    }

    if path.is_dir():
        return "bold blue", "📁"
    if path.is_symlink():
        return "cyan", "🔗"
    if path.stat().st_mode & stat.S_IXUSR:  # Executable
        return "bold green", "⚡"
    if path.name.startswith("."):  # Hidden files
        return "dim white", "🫣"

    # Check file extension
    extension = path.suffix.lower()
    for extensions, (style, icon) in file_types.items():
        if extension in extensions:
            return style, icon

    # Default files
    return "white", "📄"


def format_filename_with_style(path: Path) -> Text:
    """Format filename with Rich styling and icons."""
    style, icon = get_file_style_and_icon(path)

    # Create Rich Text object with styling
    text = Text()
    text.append(f"{icon} ", style="white")
    text.append(path.name, style=style)

    return text


def format_size_human_readable(size: int) -> str:
    """Convert file size to human-readable format."""
    kilobyte = 1024.0
    size_float = float(size)

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_float < kilobyte:
            if unit == "B":
                return f"{size_float:>3.0f}{unit}"
            return f"{size_float:>6.1f}{unit}"
        size_float /= kilobyte
    return f"{size_float:>6.1f}PB"


def create_long_listing_table(entries: list[Path]) -> Table:
    """Create a Rich table for long listing format."""
    table = Table(
        title="📁 Directory Listing",
        show_header=True,
        header_style="bold cyan",
        border_style="bright_black",
        row_styles=["", "dim"],
        expand=True,
    )

    # Add columns with descriptive names
    table.add_column("Type", style="white", width=2, justify="center")
    table.add_column("Permissions", style="white", min_width=10, max_width=12)
    table.add_column("Links", style="dim white", width=5, justify="right")
    table.add_column("Owner", style="yellow", min_width=8, max_width=15)
    table.add_column("Group", style="blue", min_width=8, max_width=15)
    table.add_column("Size", style="magenta", width=8, justify="right")
    table.add_column("Modified", style="green", width=12)
    table.add_column("Name", style="white", min_width=15)

    # Add rows for each file
    for entry_path in entries:
        try:
            file_stat: stat_result = entry_path.lstat()
        except OSError as os_error:
            # Print error message for files we can't access
            error_console.print(
                f"[red]ls: cannot access '{entry_path}': {os_error.strerror}[/red]"
            )
            continue

        # Get file info
        mode: str = stat.filemode(file_stat.st_mode)
        nlink: int = file_stat.st_nlink
        owner: str = pwd.getpwuid(file_stat.st_uid).pw_name
        group: str = grp.getgrgid(file_stat.st_gid).gr_name
        size_human: str = format_size_human_readable(file_stat.st_size)
        mtime: str = time.strftime(
            "%b %d %H:%M",
            time.localtime(file_stat.st_mtime),
        )

        # Get file styling and icon
        file_style, icon = get_file_style_and_icon(entry_path)

        # Style the permissions based on file type
        if mode.startswith("d"):
            perm_style = "bold blue"
        elif mode.startswith("l"):
            perm_style = "cyan"
        elif "x" in mode[7:]:
            perm_style = "bold green"
        else:
            perm_style = "white"

        # Create filename with icon and styling
        filename_text = Text()
        filename_text.append(f"{icon} ", style="white")
        filename_text.append(entry_path.name, style=file_style)

        # Add row to table
        table.add_row(
            icon,
            Text(mode, style=perm_style),
            str(nlink),
            owner,
            group,
            size_human,
            mtime,
            filename_text,
        )

    return table


def get_directory_size(path: Path) -> int:
    """Calculate the total size of a directory and its contents."""
    if not path.is_dir():
        return 0

    total_size = 0
    try:
        for item in path.rglob("*"):
            try:
                if item.is_file():
                    total_size += item.stat().st_size
            except (OSError, PermissionError):
                # Skip files we can't access
                continue
    except (OSError, PermissionError):
        # Skip directories we can't access
        pass

    return total_size


def create_size_sorted_table(entries: list[Path], limit: int) -> Table:
    """Create a Rich table for size-sorted listing."""
    table = Table(
        title=f"📊 Top {limit} Files/Directories by Size",
        show_header=True,
        header_style="bold cyan",
        border_style="bright_black",
        row_styles=["", "dim"],
        expand=True,
    )

    # Add columns
    table.add_column("Type", style="white", width=6, justify="center")
    table.add_column("Name", style="white", min_width=20)
    table.add_column("Size", style="magenta", width=10, justify="right")

    # Get file sizes and sort by size (descending)
    entries_with_size = []
    for entry_path in entries:
        try:
            if entry_path.is_dir():
                size = get_directory_size(entry_path)
                file_type = "DIR"
            else:
                size = entry_path.stat().st_size
                file_type = "FILE"

            entries_with_size.append((entry_path, size, file_type))
        except OSError as os_error:
            # Print error message for files we can't access
            error_console.print(
                f"[red]ls: cannot access '{entry_path}': {os_error.strerror}[/red]"
            )
            continue

    # Sort by size (descending) and take top N
    entries_with_size.sort(key=lambda x: x[1], reverse=True)
    top_entries = entries_with_size[:limit]

    # Add rows to table
    for entry_path, size, file_type in top_entries:
        # Get file styling and icon
        file_style, icon = get_file_style_and_icon(entry_path)
        size_human = format_size_human_readable(size)

        # Create filename with icon and styling
        filename_text = Text()
        filename_text.append(f"{icon} ", style="white")
        filename_text.append(entry_path.name, style=file_style)

        # Style the type column
        type_style = "bold blue" if file_type == "DIR" else "white"

        table.add_row(
            Text(file_type, style=type_style),
            filename_text,
            size_human,
        )

    return table


@click.command("richpyls", epilog="Thanks for using richpyls!")
@click.version_option(__version__)
@click.option(
    "-l",
    "long",
    is_flag=True,
    help="use a long listing format",
)
@click.option(
    "-a",
    "show_all",
    is_flag=True,
    help="do not ignore entries starting with .",
)
@click.option(
    "-t",
    "tree",
    is_flag=True,
    help="display directories in a tree-like format",
)
@click.option(
    "-s",
    "sort_by_size",
    type=int,
    help="show top N files/directories sorted by size (descending)",
)
@click.argument(
    "paths",
    nargs=-1,
    type=click.Path(exists=True),
)
def cli(
    long: bool,
    show_all: bool,
    tree: bool,
    sort_by_size: int | None,
    paths: tuple[str, ...],
) -> None:
    """List information about the FILEs (the current directory by default).

    Supports long format listing (-l), hidden files (-a), tree view (-t),
    and size-sorted listing (-s N) to show top N files by size.
    """
    if not paths:
        paths_list: list[str] = ["."]
    else:
        paths_list = list(paths)

    # Convert string paths to Path objects
    path_objects: list[Path] = [Path(p) for p in paths_list]
    multiple_paths: bool = len(path_objects) > 1

    for path_obj in path_objects:
        if multiple_paths:
            click.echo(f"{path_obj}:")

        if path_obj.is_dir():
            if tree:
                list_directory_tree(path_obj, show_all, long)
            elif sort_by_size is not None:
                list_directory_by_size(path_obj, show_all, sort_by_size)
            else:
                list_directory_entries(path_obj, show_all, long)
        else:
            list_single_file(path_obj, long)

        if multiple_paths:
            click.echo()


def list_directory_entries(path_obj: Path, show_all: bool, long_format: bool) -> None:
    """List entries in a directory."""
    try:
        entries: list[Path] = sorted(path_obj.iterdir())
    except OSError as os_error:
        error_console.print(
            f"[red]ls: cannot access '{path_obj}': {os_error.strerror}[/red]"
        )
        return

    # Filter hidden files unless show_all is True
    entries = [entry for entry in entries if show_all or not entry.name.startswith(".")]

    if long_format:
        # Create and display the long listing table
        table = create_long_listing_table(entries)
        console.print(table)
    else:
        for entry_path in entries:
            styled_name = format_filename_with_style(entry_path)
            console.print(styled_name)


def list_single_file(path_obj: Path, long_format: bool) -> None:
    """List information for a single file."""
    if long_format:
        try:
            # Check if we can access the file first
            path_obj.lstat()
            # Create table with single file
            table = create_long_listing_table([path_obj])
            console.print(table)
        except OSError as os_error:
            error_console.print(
                f"[red]ls: cannot access '{path_obj}': {os_error.strerror}[/red]"
            )
    else:
        styled_name = format_filename_with_style(path_obj)
        console.print(styled_name)


def format_file_info(file_stat: stat_result, file_name: str) -> Text:
    """Format file information for long listing display with Rich styling."""
    mode: str = stat.filemode(file_stat.st_mode)
    nlink: int = file_stat.st_nlink
    owner: str = pwd.getpwuid(file_stat.st_uid).pw_name
    group: str = grp.getgrgid(file_stat.st_gid).gr_name
    size_human: str = format_size_human_readable(file_stat.st_size)
    mtime: str = time.strftime(
        "%b %d %H:%M",
        time.localtime(file_stat.st_mtime),
    )

    # Create Rich Text object with styling
    text = Text()

    # Style permissions based on type
    if mode.startswith("d"):
        text.append(mode, style="bold blue")
    elif mode.startswith("l"):
        text.append(mode, style="cyan")
    elif "x" in mode[7:]:  # Check if executable by others
        text.append(mode, style="bold green")
    else:
        text.append(mode, style="white")

    text.append(f" {nlink:>2} ", style="dim white")
    text.append(f"{owner} ", style="yellow")
    text.append(f"{group} ", style="blue")
    text.append(f"{size_human:>8} ", style="magenta")
    text.append(f"{mtime} ", style="green")

    # Add styled filename
    path_obj = Path(file_name)
    _, icon = get_file_style_and_icon(path_obj)
    file_style, _ = get_file_style_and_icon(path_obj)
    text.append(f"{icon} ", style="white")
    text.append(file_name, style=file_style)

    return text


def list_directory_tree(
    path_obj: Path,
    show_all: bool,
    long_format: bool,
    prefix: str = "",
) -> None:
    """Display directory contents in a tree-like format with Rich styling."""
    try:
        entries: list[Path] = sorted(path_obj.iterdir())
    except OSError as os_error:
        error_console.print(
            f"[red]ls: cannot access '{path_obj}': {os_error.strerror}[/red]"
        )
        return

    # Filter hidden files unless show_all is True
    entries = [entry for entry in entries if show_all or not entry.name.startswith(".")]

    # Sort entries: directories first, then files, both alphabetically
    entries.sort(key=lambda p: (not p.is_dir(), p.name.lower()))

    for i, entry_path in enumerate(entries):
        is_last_entry = i == len(entries) - 1

        # Choose the appropriate tree character
        if is_last_entry:
            tree_char = "└── "
            next_prefix = prefix + "    "
        else:
            tree_char = "├── "
            next_prefix = prefix + "│   "

        try:
            file_stat: stat_result = entry_path.lstat()
        except OSError as os_error:
            error_console.print(
                f"[red]ls: cannot access '{entry_path}': {os_error.strerror}[/red]"
            )
            continue

        # Create Rich Text object for tree display
        tree_text = Text()
        tree_text.append(prefix, style="dim white")
        tree_text.append(tree_char, style="bright_black")

        if long_format:
            # Add file info with styling
            mode: str = stat.filemode(file_stat.st_mode)
            nlink: int = file_stat.st_nlink
            owner: str = pwd.getpwuid(file_stat.st_uid).pw_name
            group: str = grp.getgrgid(file_stat.st_gid).gr_name
            size_human: str = format_size_human_readable(file_stat.st_size)
            mtime: str = time.strftime(
                "%b %d %H:%M",
                time.localtime(file_stat.st_mtime),
            )

            # Style permissions
            if mode.startswith("d"):
                tree_text.append(mode, style="bold blue")
            elif mode.startswith("l"):
                tree_text.append(mode, style="cyan")
            elif "x" in mode[7:]:
                tree_text.append(mode, style="bold green")
            else:
                tree_text.append(mode, style="white")

            tree_text.append(f" {nlink:>2} ", style="dim white")
            tree_text.append(f"{owner} ", style="yellow")
            tree_text.append(f"{group} ", style="blue")
            tree_text.append(f"{size_human:>8} ", style="magenta")
            tree_text.append(f"{mtime} ", style="green")

        # Add styled filename with icon
        style, icon = get_file_style_and_icon(entry_path)
        tree_text.append(f"{icon} ", style="white")
        tree_text.append(entry_path.name, style=style)

        console.print(tree_text)

        # Recursively display subdirectories
        if entry_path.is_dir():
            list_directory_tree(entry_path, show_all, long_format, next_prefix)


def list_directory_by_size(path_obj: Path, show_all: bool, limit: int) -> None:
    """List entries in a directory sorted by size."""
    try:
        entries: list[Path] = sorted(path_obj.iterdir())
    except OSError as os_error:
        error_console.print(
            f"[red]ls: cannot access '{path_obj}': {os_error.strerror}[/red]"
        )
        return

    # Filter hidden files unless show_all is True
    entries = [entry for entry in entries if show_all or not entry.name.startswith(".")]

    # Create and display the size-sorted table
    table = create_size_sorted_table(entries, limit)
    console.print(table)


if __name__ == "__main__":
    cli()
