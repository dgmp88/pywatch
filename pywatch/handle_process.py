import os
import signal
import subprocess

process = None

def start(cmd):
    global process
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)

def stop():
    global process
    if process != None:
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        process = None
