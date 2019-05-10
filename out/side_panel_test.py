import json
import sys
from time import sleep

# dictation
print(json.dumps(
    {'input': 'dict_ip', 'output': 'hello',
     'audio_type': 'dictation'}
))
sys.stdout.flush()
sleep(2)

print(json.dumps(
    {'input': 'dict_ip', 'output': 'world',
     'audio_type': 'dictation'}
))
sys.stdout.flush()
sleep(4)

# error
print(json.dumps(
    {'error': 'ParseError', 'input': 'declare integer x',
     'output': 'could not parse input'}
))
sys.stdout.flush()
sleep(4)

# suggestions
print(json.dumps([
    {'input': 'declare integer x'},
    {'output': 'int x', 'replace': 'int main() {int x;}', 'cursor': 1},
    {'output': 'int ex', 'replace': 'int main() {int ex;}', 'cursor': 1},
    {'output': 'UnknowReqError', 'error': 'could not undrestand request'},
]))
sys.stdout.flush()
sleep(4)

# more errors
print(json.dumps(
    {'error': 'ReqError', 'input': 'declare variable x',
     'output': 'Name missing'}
))
sys.stdout.flush()
sleep(10)
