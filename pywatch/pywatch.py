from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from handle_process import start, stop
import ignore
import sys
import os

# Global variables
last_modified = 0
start_time = time.time()
file_changed = ''
restart_wait = 0.5 # in seconds

# Simple class that reacts to changes
class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global last_modified, file_changed
        src_path = event.src_path
        if event.is_directory and sys.platform == 'darwin':
            # On OSX, we need to do this annoyingly
            src_path = self.check_event_files(event)

        if src_path and not ignore.do_ignore(src_path):
            last_modified = time.time()
            file_changed = src_path


    def check_event_files(self, event):
        files_in_dir = [event.src_path+"/"+f for f in os.listdir(event.src_path)]
        files_in_dir = filter(lambda x: ignore.do_ignore(x) ==False, files_in_dir)
        files_in_dir = filter(lambda x: os.path.getmtime(x) > start_time, files_in_dir)
        files_in_dir = filter(lambda x: os.path.isdir(x) == False, files_in_dir)

        if len(files_in_dir) > 0:
            return max(files_in_dir, key=os.path.getmtime)
        else:
            return None

# Whatever the restart function needs to be
def restart(cmd):
    stop()
    time.sleep(0.1)
    start(cmd)
    print('%s changed, restarted' % (file_changed))

def main():
    if len(sys.argv) < 2:
        print('Usage: pywatch "runcmd"')
        raise Exception
    cmd = sys.argv[1]

    # Setup watchdog
    observer = Observer()
    event_handler = MyHandler()
    observer.schedule(event_handler, '.', recursive=True)
    observer.start()

    # The main 'loop'
    try:
        global last_modified
        start(cmd)
        while True:
            if last_modified != 0:
                if time.time() - last_modified > restart_wait:
                    restart(cmd)
                    last_modified = 0
            time.sleep(0.1)

    # Exit cleanly
    except KeyboardInterrupt:
        observer.stop()
        stop()
    observer.join()

if __name__ == '__main__':
    main()
