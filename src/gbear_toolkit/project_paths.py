import os
import tkinter as tk
from tkinter import filedialog

class ProjectPaths():
    def __init__(self, main_dir: str):
        self.root = self.get_project_root(main_dir)
        if self.root is None:
            raise FileNotFoundError(f"[ERROR] Could not find a '{main_dir}' folder at or above {os.getcwd()}")
    
    def get_project_root(self, main_dir: str):
        current_directory = os.getcwd()
        project_root = None
        while not project_root:
            directory_name = os.path.basename(current_directory)
            if main_dir == directory_name:
                project_root = current_directory
                print(f"[INFO] Project root initialized at: {project_root}")
                return project_root
            if directory_name == '':
                print('[ERROR] Unable to find specified directory')
                return None
            else:
                current_directory = os.path.dirname(current_directory)
                continue

    def path_to(self, *steps):
        path = os.path.join(self.root, *steps)
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        return os.path.abspath(path)

    def user_select(self, type: str = 'file'):
        root = tk.Tk()
        root.title("Select")
        root.attributes('-alpha', 0.0)      # invisible, but still shows in taskbar
        root.attributes('-topmost', True)   # bring it to the front
        root.lift()
        root.focus_force()
        try:
            if type == 'file':
                path = filedialog.askopenfilename(parent=root, title="Select a file")
            elif type == 'folder':
                path = filedialog.askdirectory(parent=root, title="Select a folder")
            else:
                raise ValueError(f"type must be 'file' or 'folder', got {type!r}")
        finally:
            root.destroy()
        return os.path.abspath(path) if path else None

