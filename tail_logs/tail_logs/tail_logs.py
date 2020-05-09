#!/usr/bin/env python3
# 2020-05-09, wildi.markus@bluewin.ch

__author__ = 'wildi.markus@bluewin.ch'

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from os.path import expanduser
import tail_logs_worker as tl
import sys
import time
import os

class EventHandler(FileSystemEventHandler):
    def on_created(self, event):
        tl.lg.debug(f'event type: {event.event_type}  path : {event.src_path}')
        tl.terminate = True
        tail = tl.Tail_logs_worker(lg = tl.lg, args = tl.args, fn = event.src_path)
        tail.tail()
def main():

    event_handler = EventHandler()
    observer = Observer()
    path = os.path.join(expanduser("~"), tl.args.base_path)
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

    
    
if __name__ == '__main__':

    main()

