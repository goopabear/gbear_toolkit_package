import os
import shutil

def create_at(abs_path: str, name: str):
    new_folder = os.path.join(abs_path, name)
    try:
        os.makedirs(new_folder, exist_ok=True)
        print(f"Folder created at:\n{os.path.basename(new_folder)}\n")
        return new_folder
    except Exception as e:
        print(f"Error creating '{new_folder}' folder: {e}\n")
        return None

def copy(src_path: str, dest_path: str, src: str = 'csv', dest: str = 'tmp'):
    source = os.path.join(src_path, src)
    destination = os.path.join(dest_path, dest)
    try:
        shutil.copytree(source, destination, dirs_exist_ok=True)
        print(f"Files copied into new folder at:\n{os.path.basename(destination)}\n")
        return
    except Exception as e:
        print(f"Error copying CSV files: {e}\n")
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
        print(f"Error listing files in '{abs_path}': {e}\n")
        return None

def delete(abs_path: str, name: str):
    tmp_folder = os.path.join(abs_path, name) 
    # Relative path from root to "tmp"
    # Can include additional arguments as steps up
    try:
        shutil.rmtree(tmp_folder)
        # shutil.rmtree() works on directories, given an absolute path.
        # os.remove() works in files, given an absolute path.
        print("Setup Initialized:\n'tmp' folder deleted\n")

    except Exception as e:
        print(f"Error deleting 'tmp' folder: {e}\n")