import asyncio
import os
import ssl
from pathlib import Path
from collections import deque
from typing import Tuple, Any

import aiohttp
import certifi
import typer
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    ProgressColumn,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
    Task,
)
from rich.table import Table
from rich.text import Text
from rich.columns import Columns

from gcloud.aio.storage import Storage

from ..config import ConfigManager, DATA_DIR

import multiprocessing
from functools import partial
import time
from queue import Empty
import shutil
import subprocess

DEFAULT_INDEX_FILE = DATA_DIR / "migration_index.txt"
DEFAULT_PROGRESS_FILE = DATA_DIR / "migration_progress.txt"

console = Console()


def _generate_index_lines_for_chunk(file_paths: list[Path], source_dir: Path, gcs_target_prefix: str) -> list[str]:
    """
    A worker process that takes a list (chunk) of file paths and returns a
    list of formatted strings for the index file.
    """
    results = []
    for file_path in file_paths:
        relative_path = str(file_path.relative_to(source_dir)).replace(os.sep, '/')
        gcs_object_name = f"{gcs_target_prefix}/{relative_path}" if gcs_target_prefix else relative_path
        results.append(f"{file_path}|{gcs_object_name}\n")
    return results


def _count_total_files_and_feed_queue(source_path: Path, queue: multiprocessing.Queue) -> int:
    """
    Scans the source path to count total files and puts file paths into a queue.
    This runs in a separate process to avoid blocking the main UI thread.
    Returns the total number of files found.
    """
    count = 0
    for root, _, files in os.walk(source_path):
        for name in files:
            file_path = Path(root) / name
            queue.put(file_path)
            count += 1
    return count

def _worker_process_from_queue(file_path: Path | None, source_dir: Path, gcs_target_prefix: str) -> str | None:
    """
    A worker function that processes a single file path.
    Designed to be used with pool.imap_unordered.
    """
    if file_path is None:
        return None
    try:
        relative_path = str(file_path.relative_to(source_dir)).replace(os.sep, '/')
        gcs_object_name = f"{gcs_target_prefix}/{relative_path}" if gcs_target_prefix else relative_path
        return f"{file_path}|{gcs_object_name}\n"
    except Exception:
        return None


def _get_total_files_find(source_path: Path) -> int | None:
    """Get the total number of files using 'find' and 'wc -l' for a fast count."""
    try:
        find_cmd = ["find", str(source_path), "-type", "f"]
        wc_cmd = ["wc", "-l"]

        find_process = subprocess.Popen(find_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        wc_process = subprocess.Popen(wc_cmd, stdin=find_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if find_process.stdout:
            find_process.stdout.close()
        
        output, _ = wc_process.communicate()
        find_process.wait()

        if wc_process.returncode == 0 and find_process.returncode == 0:
            return int(output.strip())
        else:
            return None
    except (ValueError, FileNotFoundError):
        return None

def _use_find_command(source_path: Path) -> bool:
    """Check if 'find' command is available and executable."""
    return shutil.which("find") is not None

def file_iterator_find(source_path: Path):
    """Generator function that yields file paths using the 'find' command."""
    command = ["find", str(source_path), "-type", "f"]
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
        if process.stdout:
            for line in process.stdout:
                yield Path(line.strip())

def file_iterator_walk(source_path: Path):
    """Generator function that yields file paths from the source directory using os.walk."""
    for root, _, files in os.walk(source_path):
        for name in files:
            yield Path(root) / name


class PipelineStatusColumn(ProgressColumn):
    """Renders task status, showing total as it's discovered."""

    def render(self, task: "Task") -> Text:
        """Render the task status."""
        if task.total is None or task.total == 0:
            return Text(f"{task.completed:,} files processed", style="progress.description")
        
        return Text(
            f"{task.completed:,} of {task.total:,} files processed",
            style="progress.description",
        )


def _file_walker_producer(source_path: Path, file_queue: multiprocessing.Queue, total_files_val: multiprocessing.Value):
    """
    Walks the directory tree, puts file paths into the queue, and updates a shared total count.
    This runs in a dedicated process.
    """
    count = 0
    for root, _, files in os.walk(source_path):
        for name in files:
            file_queue.put(Path(root) / name)
            count += 1
            total_files_val.value = count


def create_scan_index(config: ConfigManager) -> int:
    """
    Scans a source directory in parallel using a memory-efficient producer-consumer
    pipeline with multiprocessing.Pool, suitable for directories with millions of files.
    """
    source_path = Path(config.get("source_dir")).resolve()
    gcs_target_prefix = config.get("gcs_target_prefix", required=False, default="")
    index_file = Path(config.get("index_file", required=False, default=DEFAULT_INDEX_FILE))
    scan_workers = int(config.get("scan_workers", required=False, default=os.cpu_count() or 1))
    index_file.parent.mkdir(parents=True, exist_ok=True)

    console.print(f"🔍 Starting scan of [cyan]{source_path}[/cyan]...")
    console.print(f"   Index will be written to [green]{index_file}[/green].")

    processed_count = 0
    progress = Progress(
        TextColumn("[bold green]Processing...[/bold green]"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        "•",
        PipelineStatusColumn(),
        console=console,
    )
    
    # Decide which iterator to use and try to get a total count
    use_find = _use_find_command(source_path)
    total_files = None

    if use_find:
        console.log("⚡️ Using fast 'find' command for file discovery.")
        file_iterator = file_iterator_find(source_path)
        total_files = _get_total_files_find(source_path)
        if total_files is not None:
            console.log(f"📊 Found {total_files:,} total files.")
        else:
            console.log("[yellow]Could not determine total file count beforehand. Progress bar will be indeterminate.[/yellow]")
    else:
        file_iterator = file_iterator_walk(source_path)
        console.log("🐢 'find' command not available. Using slower 'os.walk'. Progress bar will be indeterminate.")


    try:
        with progress:
            task_id = progress.add_task("scan", total=total_files)
            
            with open(index_file, 'w') as f, multiprocessing.Pool(processes=scan_workers) as pool:
                worker_func = partial(
                    _worker_process_from_queue,
                    source_dir=source_path,
                    gcs_target_prefix=gcs_target_prefix
                )
                
                results_iterator = pool.imap_unordered(worker_func, file_iterator, chunksize=100)
                
                for result in results_iterator:
                    if result:
                        f.write(result)
                        processed_count += 1
                    
                    # Advance progress by one for each file the iterator yields to the pool
                    # This gives a sense of discovery progress when total is unknown
                    progress.update(task_id, advance=1)
            
            final_total = total_files if total_files is not None else processed_count
            progress.update(task_id, completed=processed_count, total=final_total, description="[bold green]Scan Complete[/bold green]")

    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred during scan: {e}[/bold red]")
        # Potentially re-raise or handle as needed
        raise
        
    return processed_count


async def _upload_worker(
    line_info: str,
    bucket_name: str,
    storage: Storage,
) -> tuple[str, bool, int | str]:
    """
    Asynchronous worker to upload a single file.
    Returns a tuple of (line_info, success, result).
    Result is file size on success, error message on failure.
    """
    if '|' not in line_info:
        return (line_info, False, "Invalid line format in index file (missing '|')")

    local_path_str, gcs_object_name = line_info.split('|', 1)
    local_path = Path(local_path_str)

    try:
        await storage.upload(
            bucket_name,
            gcs_object_name,
            str(local_path)
        )
        return (line_info, True, local_path.stat().st_size)
    except Exception as e:
        error_type = type(e).__name__
        error_message = str(e).splitlines()[0] if str(e).strip() else error_type
        return (line_info, False, error_message)


async def _progress_file_writer(queue: asyncio.Queue, progress_file: Path) -> None:
    """
    Asynchronous worker that listens to a queue and writes completed paths to the progress file.
    """
    # Open the file once and write as items come in.
    with open(progress_file, 'a') as f:
        while True:
            path_to_write = await queue.get()
            if path_to_write is None:
                # Sentinel value received, terminate.
                break
            f.write(f"{path_to_write}\n")
            f.flush()


async def _check_gcs_bucket_accessibility(storage: Storage, bucket_name: str):
    """Check if the GCS bucket is accessible."""
    console.print(f"✈️  Running pre-flight check for GCS bucket: [bold cyan]{bucket_name}[/]...")
    try:
        # To check for bucket existence and permissions, we get the bucket
        bucket = storage.get_bucket(bucket_name)
        await bucket.list_blobs()
        return True
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] GCS pre-flight check failed. Cannot access bucket '{bucket_name}'. Reason: {e}")
        return False


async def start_migration(config: ConfigManager):
    """
    Initializes and runs the file migration using asyncio for high concurrency.
    """
    bucket_name = config.get("gcs_bucket_name")
    max_concurrency = int(config.get("max_concurrency", required=False, default=1000))
    gcs_timeout_seconds = int(config.get("gcs_timeout_seconds", required=False, default=300))
    index_file = Path(config.get("index_file", required=False, default=DEFAULT_INDEX_FILE))
    progress_file = Path(config.get("progress_file", required=False, default=DEFAULT_PROGRESS_FILE))
    service_account_key_file = config.get("gcs_service_account_key_file", required=False)

    progress_file.parent.mkdir(parents=True, exist_ok=True)

    # --- SSL Context and Session Setup for robust connectivity ---
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    timeout = aiohttp.ClientTimeout(total=gcs_timeout_seconds)
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=ssl_context), timeout=timeout
    ) as session:
        # --- Async Pre-flight Check ---
        async with Storage(service_file=service_account_key_file, session=session) as storage:
            if not await _check_gcs_bucket_accessibility(storage, bucket_name):
                raise ConnectionError(f"GCS pre-flight check failed. Cannot access bucket '{bucket_name}'.")
            console.print("✅ Pre-flight check passed. Bucket is accessible.")

        # --- File List Preparation ---
        try:
            with open(index_file, 'r') as f:
                all_files = set(line for line in f.read().splitlines() if line)
        except FileNotFoundError:
            raise FileNotFoundError(f"Index file not found at {index_file}. Please run the 'scan' command first.")

        completed_files = set()
        if progress_file.exists():
            with open(progress_file, 'r') as f:
                completed_source_paths = set(f.read().splitlines())
            all_files_map = {line.split('|')[0]: line for line in all_files}
            completed_files = {all_files_map[src_path] for src_path in completed_source_paths if src_path in all_files_map}
        
        remaining_lines = list(all_files - completed_files)
        
        if not remaining_lines:
            console.print("✅ No new files to migrate. Everything is up to date.")
            return

        console.print(f"Found {len(all_files):,} total files. {len(completed_files):,} already migrated.")
        console.print(f"🚀 Starting migration of [yellow]{len(remaining_lines):,}[/yellow] remaining files with [cyan]{max_concurrency}[/cyan] concurrent tasks...")

        # --- UI and Task Management ---
        progress_file_writer_queue = asyncio.Queue()
        recent_files = deque(maxlen=5)
        successful_uploads = 0
        failed_uploads = 0

        progress_bar = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TransferSpeedColumn(),
            "•",
            TextColumn("{task.completed}/{task.total} files"),
            "•",
            TimeRemainingColumn(),
        )
        
        def generate_status_table() -> Table:
            table = Table(box=None, show_header=False, show_edge=False, expand=True)
            table.add_column("Info")
            files_to_show = list(reversed(list(recent_files)))
            for status, file_path in files_to_show:
                table.add_row(f"{status} {file_path}")
            for _ in range(5 - len(files_to_show)):
                table.add_row("")
            return table

        progress_group = Group(progress_bar, generate_status_table())
        task_id = progress_bar.add_task("[green]Migrating files...", total=len(remaining_lines))
        
        aborted = False
        
        with Live(progress_group, console=console, refresh_per_second=10, transient=True) as live:
            try:
                async with Storage(service_file=service_account_key_file, session=session) as storage:
                    progress_writer_task = asyncio.create_task(_progress_file_writer(progress_file_writer_queue, progress_file))

                    tasks = [
                        asyncio.create_task(_upload_worker(line, bucket_name, storage))
                        for line in remaining_lines
                    ]
                    
                    for future in asyncio.as_completed(tasks):
                        line_info, success, result = await future
                        short_path = '/'.join(line_info.split('|')[0].split('/')[-3:])

                        if success:
                            file_size = result
                            await progress_file_writer_queue.put(line_info.split('|')[0])
                            successful_uploads += 1
                            progress_bar.update(task_id, advance=1, total_bytes=file_size)
                            recent_files.append(("[green]✔[/green]", f"[green]{short_path}[/green]"))
                        else:
                            error_message = result
                            failed_uploads += 1
                            progress_bar.update(task_id, advance=1)
                            recent_files.append(("[bold red]✖[/bold red]", f"[red]{short_path}[/red] [dim]({error_message})[/dim]"))

                        live.renderable.renderables[1] = generate_status_table()

            except (KeyboardInterrupt, asyncio.CancelledError):
                aborted = True            
            finally:
                progress_bar.stop()
                if 'progress_writer_task' in locals() and progress_writer_task.done() is False:
                    await progress_file_writer_queue.put(None)
                    await progress_writer_task
        
        # --- Recompose Final Static View ---
        final_status_table = generate_status_table()

        if aborted or failed_uploads > 0:
            console.print(final_status_table)    

        if aborted:
            console.print("\n[bold yellow]Migration aborted by user.[/bold yellow]\n")
        elif failed_uploads > 0:
            console.print()

        summary_lines = []
        panel_title = "Migration Summary"
        border_style = "green"

        if aborted:
            panel_title += " (Aborted)"
            border_style = "yellow"
        elif failed_uploads > 0:
            panel_title += " (Completed with Errors)"
            border_style = "yellow"
        else:
            panel_title += " (Success)"

        summary_lines.append(f"[green]Successful uploads: {successful_uploads}[/green]")
        summary_lines.append(f"[red]Failed uploads: {failed_uploads}[/red]")
        
        if aborted:
            summary_lines.append("\n[yellow]Migration was stopped before all files could be processed.[/yellow]")
        elif failed_uploads > 0:
            summary_lines.append("\n[dim]Review the list above for details on failed files.[/dim]")

        summary_text_obj = Text.from_markup("\n".join(summary_lines), justify="left")
        console.print(Panel(Columns([summary_text_obj]), title=f"[bold]{panel_title}[/bold]", border_style=border_style, expand=False, padding=(1, 2), width=64)) 