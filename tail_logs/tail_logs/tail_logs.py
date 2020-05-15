#!/usr/bin/env python3
# 2020-05-09, wildi.markus@bluewin.ch

__author__ = 'wildi.markus@bluewin.ch'

import multiprocessing

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from os.path import expanduser
import tail_logs_worker as tl
import sys
import time
import os

class Tailer(multiprocessing.Process):
    
    def __init__(self, fn = None):

        multiprocessing.Process.__init__(self)
        self.fn = fn

    def run(self):
        tail = tl.Tail_logs_worker(lg = tl.lg, args = tl.args, fn = self.fn)
        tail.tail()


class EventHandler(FileSystemEventHandler):
    def on_created(self, event):
        tl.lg.info(f'event type: {event.event_type}  path : {event.src_path}')
        t = Tailer(fn = event.src_path)
        t.start()
        # ... and forget

def main():

    event_handler = EventHandler()
    observer = Observer()
    path = os.path.join(expanduser("~"), tl.args.base_path)
    tl.lg.info('watchdog on: {}'.format(path))
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

