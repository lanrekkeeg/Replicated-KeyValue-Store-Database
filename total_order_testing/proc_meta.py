import os
import sys
import psutil


def kill_child_proc(ppid):
    print("Parent:",ppid)
    for process in psutil.process_iter():
        _ppid = process.ppid()
        if _ppid == ppid:
            _pid = process.pid
            if sys.platform == 'win32':
                process.terminate()
            else:
                print("Child Process ID:".format(_pid))
                os.system('kill -9 {0}'.format(_pid))
                
id = int(sys.argv[1])
kill_child_proc(id)