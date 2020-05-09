#
# 2020-05-09, wildi.markus@bluewin.ch
#
# argparse anywhere
#
__author__ = 'wildi.markus@bluewin.ch'

import argparse
import sys
import os
import logging
import glob
import time
import errno
import platform


def make_dir(path):
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as e: 
        if e.errno != errno.EEXIST:
            logger.error('exiting, can not create directory: {}'.format(path))
            sys.exit(1)

parser= argparse.ArgumentParser(prog=sys.argv[0], description='Find mount\'s HA, Dec position from INDI log')
parser.add_argument('--log-file-path', dest='log_file_path', action='store', default='C:\\temp',type=str, help=': %(default)s, directory where valid XML files are stored')
parser.add_argument('--level', dest='level', default='INFO', choices = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help=': %(default)s, debug level')
parser.add_argument('--toconsole', dest='toconsole', action='store_true', default=False, help=': %(default)s, log to console')
parser.add_argument('--processes', dest='processes', action='store', default=None, type = int, help=': %(default)s, number of processes, of not specified processes equals to cpu threads')
parser.add_argument('--base-path', dest='base_path', action='store', default='.indi/logs',type=str, help=': %(default)s, INDI log file path relative to $HOME')

args=parser.parse_args()

pth, fn = os.path.split(sys.argv[0])
stm=fn.replace('.py','')

if 'Linux' in platform.system():
    p_log= './{}.log'.format(stm)
else:
    if not os.path.exists(args.log_file_path):
        print('exiting, non existing log file path: {}, create it manually'.format(args.log_file_path))
        sys.exit(1)
    p_log= os.path.join(args.log_file_path, '{}.log'.format(stm))

logformat= '%(asctime)s:%(name)s:%(levelname)s:%(message)s'
logging.basicConfig(filename=str(p_log), level=args.level.upper(), format=logformat)
logger = logging.getLogger()

if args.toconsole:
    # http://www.mglerner.com/blog/?p=8
    soh = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(levelname)s : %(message)s')
    soh.setFormatter(formatter)
    args.level='DEBUG'
    soh.setLevel(args.level)
    logger.addHandler(soh)

    
