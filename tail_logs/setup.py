''' 
 2020-05-09, wildi 
 setup for module tail_logs 

'''

__author__ = 'wildi.markus@bluewin.ch'

import setuptools
import shutil
import os
import datetime

with open("README.md", "r") as fh:
    long_description = fh.read()

     
for fn in os.listdir('.'):
    if fn.endswith('.log'):
        os.remove(fn)
try:
    for fn in os.listdir('./dist'):
        try:
            os.remove(os.path.join('./dist', fn))
        except OSError as e:
            pass
except FileNotFoundError:
    pass

for root, dirs, files in os.walk('.'):
    for fn in files:
        if fn.endswith("~"):
             os.remove(os.path.join(root, fn))

setuptools.setup(
    name="tail_logs-pkg-wildi", 
    version="0.0.1",
    author="Markus Wildi",
    author_email="wildi-markus@bluewin.ch",
    description="Tail and analyze log files, e.g. calculate HA and Dec of the mount",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wildi/polar_alignment_reduction/",
    packages=setuptools.find_packages(),
    scripts=['tail_logs/tail_logs.py'],
    entry_points={
        'console_scripts': [
            'tail_logs=tail_logs:main',
        ]
      },
    classifiers=[
        "Programming Language :: Python :: 3.7.5",
        "License :: GPL v3.x",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7.5',
)
