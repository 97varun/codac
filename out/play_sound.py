import sys
from playsound import playsound

if len(sys.argv) != 2:
    print('incorrect arguments')
playsound(sys.argv[1])
