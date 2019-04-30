import sys
import os

path = os.path.dirname(os.path.realpath(__file__))
errorLog = open(path + "/stderr.txt", "w", buffering = 0)
errorLog.write("Starting Error Log")
sys.stderr = errorLog
stdoutLog = open(path + "/stdout.txt", "w", buffering = 0)
stdoutLog.write("Starting Standard Out Log")
sys.stdout = stdoutLog

from LiveDCA import LiveDCA

def create_instance(c_instance):
    return LiveDCA(c_instance)
