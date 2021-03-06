import os
import sys
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from . import ignore
from .handle_process import start, stop

# Global variables
last_modified = 0
start_time = time.time()
file_changed = ''
restart_wait = 0.5  # in seconds

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
        files_in_dir = self.get_files_in_dir(event)

        files_in_dir = [f for f in files_in_dir if not ignore.do_ignore(f)]
        files_in_dir = [
            f for f in files_in_dir if os.path.getmtime(f) > start_time]
        files_in_dir = [f for f in files_in_dir if not os.path.isdir(f)]

        if len(files_in_dir) > 0:
            return max(files_in_dir, key=os.path.getmtime)
        else:
            return None

    def get_files_in_dir(self, event):
        # This seems to crash sometimes, try to catch it
        i = 0
        err = None
        while i < 3:
            try:
                return [event.src_path+"/"+f for f in os.listdir(event.src_path)]
            except OSError as error:
                err = error
                time.sleep(0.2)
            i += 1
        raise err


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
