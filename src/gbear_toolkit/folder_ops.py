import os
import shutil

def create_at(abs_path: str, name: str):
    new_folder = os.path.join(abs_path, name)
    try:
        os.makedirs(new_folder, exist_ok=True)
        print(f"[INFO] Folder created at: {os.path.basename(new_folder)}")
        return new_folder
    except Exception as e:
        print(f"[ERROR] Error creating '{new_folder}' folder: {e}")
        return None

def copy(src_path: str, dest_path: str, src: str = 'csv', dest: str = 'tmp'):
    source = os.path.join(src_path, src)
    destination = os.path.join(dest_path, dest)
    try:
        shutil.copytree(source, destination, dirs_exist_ok=True)
        print(f"[INFO] Files copied into new folder at: {os.path.basename(destination)}")
        return
    except Exception as e:
        print(f"[ERROR] Error copying CSV files: {e}")
        return

def list_files(abs_path: str):
    try:
        entries = os.listdir(abs_path)
        files = []
        for entry in entries:
            full_path = os.path.join(abs_path, entry)
            if os.path.isfile(full_path):
                files.append(entry)
        return files
    except Exception as e:
        print(f"[ERROR] Error listing files in '{abs_path}': {e}")
        return None

def delete(abs_path: str, name: str):
    tmp_folder = os.path.join(abs_path, name) 
    # Relative path from root to "tmp"
    # Can include additional arguments as steps up
    try:
        shutil.rmtree(tmp_folder)
        # shutil.rmtree() works on directories, given an absolute path.
        # os.remove() works in files, given an absolute path.
        print(f"[INFO] {name!r} folder deleted")

    except Exception as e:
        print(f"[ERROR] Error deleting {name!r} folder: {e}")