import argparse
from .cleaner import get_junk_files, delete_junk

def human_readable_size(size_bytes):
    for unit in ['B','KB','MB','GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def main():
    parser = argparse.ArgumentParser(description="Clean Python project junk files")
    parser.add_argument('--path', type=str, default='.', help='Path to clean')
    parser.add_argument('--dry-run', action='store_true', help='Only show files to be deleted')
    parser.add_argument('--confirm', action='store_true', help='Actually delete files')
    
    args = parser.parse_args()

    print(f"\n🔍 Scanning {args.path}...\n")
    junk_files = get_junk_files(args.path)

    if not junk_files:
        print("✅ Nothing to clean.")
        return

    for item in junk_files:
        print(f"🗑️  {item}")

    print(f"\n🧮 Total files/folders: {len(junk_files)}")

    if args.confirm:
        size = delete_junk(junk_files)
        print(f"\n✅ Deleted. Space freed: {human_readable_size(size)}")
    elif args.dry_run:
        total = sum([os.path.getsize(f) if os.path.isfile(f) else 0 for f in junk_files])
        print(f"\n💡 Dry Run: {human_readable_size(total)} would be freed.")
    else:
        print("\n⚠️ Use --dry-run or --confirm to take action.")

if __name__ == "__main__":
    main()
