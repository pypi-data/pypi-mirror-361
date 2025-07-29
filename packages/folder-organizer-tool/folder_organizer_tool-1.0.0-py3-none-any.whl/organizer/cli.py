import argparse
from organizer.core import organize_folder

def main():
    parser = argparse.ArgumentParser(
        description='CLI based file organizer - Organizes files by extension.'
    )
    
    parser.add_argument('--path', required=True, help='Path of the folder to organize')
    parser.add_argument('--dry-run', action='store_true', help='Simulate action without making actual changes')
    
    args = parser.parse_args()
    organize_folder(args.path, dry_run=args.dry_run)
