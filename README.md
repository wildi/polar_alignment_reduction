# Polar alignment reduction
This repository provides tools to ease the verifying process of Ekos/INDI's polar alignment.

Intended audience are people who are working on this topic and not the general public although they are welcomed.

#Package tail_logs
The primary purpose of tail_logs is to make INDI driver's log file more accessible in a rapid compile/debug cycle environment. The script combines Python's watchdog with tailer modules. Once a new log file has started it displayed in the same terminal window.

The second purpose is to collect raw ccd simulator information and to calculate HA and Dec of the mount's hour axis. 

#Installation for the impatient (on Linux):
Change to the directory, where this README.md is found.

```
cd tail_logs
pip3 install -r requirements.txt
py3clean . && python3 setup.py sdist bdist_wheel && pip3 install . && tail_logs --toc --level DEBUG
```

Then start KStars/Ekos/INDI.

##Give it a try:

Once installed the script is on $PATH. Start

```
tail_logs --toconsole --level DEBUG
```
and then start Ekos/INDI including the ccd simulator. Take two images a couple of 15 seconds apart and see the results of the calculation as

```
...
INFO : center   RA: +02:56:06.7,     dec: +89:20:49.2, HA: -03:04:22.1, decimal: -46.09188878084741
INFO : mount gamma: +00:40:27.3, decimal: 0.6742389638617831
INFO : mount    HA: +11:07:09.3,     dec: +89:19:32.7
INFO : mount    Az: +00:00:42.4,     Alt: +46:48:02.0
```

##Help:

```
usage: /home/wildi/.local/bin/tail_logs [-h] [--log-file-path LOG_FILE_PATH]
                                        [--level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                                        [--toconsole] [--processes PROCESSES]
                                        [--base-path BASE_PATH]

Find mount's HA, Dec position from INDI log

optional arguments:
  -h, --help            show this help message and exit
  --log-file-path LOG_FILE_PATH
                        : C:\temp, directory where valid XML files are stored
  --level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        : INFO, debug level
  --toconsole           : False, log to console
  --processes PROCESSES
                        : None, number of processes, of not specified
                        processes equals to cpu threads
  --base-path BASE_PATH
                        : .indi/logs, INDI log file path relative to $HOME
```
