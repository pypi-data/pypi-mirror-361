import os
import shutil
from pathlib import Path
from rich.console import Console
from rich.text import Text

console = Console()

DEFAULT_MAP = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".svg"],
    "Documents": [".pdf", ".docx", ".txt", ".xlsx"],
    "Music": [".mp3", ".wav"],
    "Code": [".py", ".js", ".html", ".css", ".ts", "jsx", "tsx"],
    "Archives": [".zip", ".tar", ".gz"],
    "Binary": [".exe", ".dmg"],
    "Videos": [".mp4", ".mov", ".avi"]
}

def get_category_name(extension):
    for category, values in DEFAULT_MAP.items():
        if extension in values:
            return category
    return "Others"

def organize_folder(path, dry_run):
    # Get the target diectory to scan
    target_path = Path(path)
    
    # Check if the path exists and its a directory
    if not target_path.exists() or not target_path.is_dir():
        console.print(f"[red]❌ ERROR:[/red] Path '{path}' is invalid or does not exist.")
        return
    
    # Check if this path conatins files
    files = [f for f in target_path.iterdir() if f.is_file()]
    
    if not files:
        console.print("[yellow]⚠️ No files to organize.[/yellow]")
        return
    
    # Loop over the each file
    for file in files:
        # Grab the file extension
        extension = file.suffix
        # Get organization category by extension
        category = get_category_name(extension)
        
        # Construct the desination folder target_path/{category}
        destination_folder = target_path / category
        
        # Construct the desination file full path destination_folder/{file.name}
        destination_file = destination_folder / file.name
        
        if dry_run:
            console.print(f"[cyan][DRY-RUN][/cyan] Would move: '{file.name}' → [bold]{category}/[/bold]")
        else:
            # Safe check, create the directory if not exists
            destination_folder.mkdir(exist_ok=True)
            try:
                # Move the file to respective desination
                shutil.move(str(file), str(destination_file))
                console.print(f"[green]✔ Moved:[/green] {file.name} → [bold]{category}/[/bold]")
            except Exception as e:
                console.print(f"[yellow]⚠️ Skipped:[/yellow] {file.name} (reason: {e})")

