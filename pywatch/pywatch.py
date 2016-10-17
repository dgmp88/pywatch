from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from handle_process import start, stop
import ignore
import sys
import os


# Global variables
last_modified = 0
restart_wait = 0.5 # in seconds

# Simple class that reacts to changes
class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global last_modified
        if event.is_directory:
            return
        if not ignore.do_ignore(event.src_path):
            print event.src_path
            last_modified = time.time()

# Whatever the restart function needs to be
def restart(cmd):
    stop()
    time.sleep(0.1)
    start(cmd)
    print 'restarted'

def main():
    if len(sys.argv) < 2:
        print 'Usage: pywatch "runcmd"'
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
