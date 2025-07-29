import os
import glob

def human_readable_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"

def main(args):
    if not args:
        print("Usage:\n  faiz count * [--index] [--deep]\n  faiz count <pattern>\n  faiz count folder")
        return

    show_index = "--index" in args
    deep_search = "--deep" in args

    # Remove flags from args to avoid confusion
    filtered_args = [arg for arg in args if arg not in {"--index", "--deep"}]

    if not filtered_args:
        print("❌ Missing arguments.\nUsage:\n  faiz count * [--index] [--deep]\n  faiz count <pattern>\n  faiz count folder")
        return

    command = filtered_args[0]

    # 🔹 1. Folder count only ➔ faiz count folder
    if command == "folder":
        search_path = "**" if deep_search else "."
        folder_count = sum(1 for root, dirs, files in os.walk(search_path) for d in dirs)
        print(f"📁 Total folders{' (deep search)' if deep_search else ''}: {folder_count}")
        return

    # 🔹 2. Full category count ➔ faiz count * 
    if command == "*":
        categories = {
            "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".avif"},
            "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"},
            "Video": {".mp4", ".avi", ".mkv", ".mov", ".flv", ".wmv"},
            "Documents": {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".md"},
        }

        counts = {name: 0 for name in categories}
        sizes = {name: 0 for name in categories}
        counts["Other Files"] = 0
        sizes["Other Files"] = 0
        folder_count = 0

        indexed_list = []

        entries = []
        if deep_search:
            for root, dirs, files in os.walk("."):
                for name in dirs + files:
                    entries.append(os.path.join(root, name))
        else:
            entries = [entry.path for entry in os.scandir()]

        for idx, path in enumerate(entries, start=1):
            name = os.path.basename(path)
            if os.path.isdir(path):
                folder_count += 1
                if show_index:
                    indexed_list.append(f"{idx}. 📁 {name}/")
            elif os.path.isfile(path):
                ext = os.path.splitext(name.lower())[1]
                size = os.path.getsize(path)
                for cat, exts in categories.items():
                    if ext in exts:
                        counts[cat] += 1
                        sizes[cat] += size
                        break
                else:
                    counts["Other Files"] += 1
                    sizes["Other Files"] += size

                if show_index:
                    indexed_list.append(f"{idx}. 📄 {name} — {human_readable_size(size)}")

        print(f"📁 Folders: {folder_count}")
        total_size = 0
        for cat, num in counts.items():
            size = sizes[cat]
            total_size += size
            print(f"📄 {cat}: {num} files — {human_readable_size(size)}")

        total_items = folder_count + sum(counts.values())
        print(f"\n🔢 Total entries (files + folders): {total_items}")
        print(f"💾 Total size of all files: {human_readable_size(total_size)}")

        if show_index and indexed_list:
            print("\n📝 Index of Files and Folders:")
            print("-" * 30)
            for line in indexed_list:
                print(line)

        return

    # 🔹 3. Pattern match ➔ faiz count <pattern>
    pattern = command
    search_pattern = f"**/{pattern}" if deep_search else pattern
    matching = glob.glob(search_pattern, recursive=deep_search)

    file_count = sum(1 for p in matching if os.path.isfile(p))
    folder_count = sum(1 for p in matching if os.path.isdir(p))
    total_size = sum(os.path.getsize(p) for p in matching if os.path.isfile(p))

    print(f"📂 Total matching entries for '{pattern}'{' (deep search)' if deep_search else ''}: {len(matching)}")
    print(f"   - Files:   {file_count}")
    print(f"   - Folders: {folder_count}")
    print(f"💾 Total size of matching files: {human_readable_size(total_size)}")

