from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import shutil
import time

VAULT_PATH = Path(r"D:\Hackathon 0\Bronze Tier\AI_Employee_Vault")
DROP_FOLDER = Path("drop_zone")

class DropHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        
        source = Path(event.src_path)
        dest = VAULT_PATH / "Needs_Action" / source.name
        shutil.copy2(source, dest)
        print(f"File moved to Needs_Action: {source.name}")

if __name__ == "__main__":
    DROP_FOLDER.mkdir(exist_ok=True)
    
    observer = Observer()
    observer.schedule(DropHandler(), str(DROP_FOLDER), recursive=False)
    observer.start()
    
    print("Watcher running...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()