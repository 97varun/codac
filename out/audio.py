from __future__ import division

import re
import sys
import os
import json

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import pyaudio
from six.moves import queue
from main import get_action
from time import sleep

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)


def listen_print_loop(responses):
    """Iterates through server responses and prints them.

    The responses passed is a generator that will block until a response
    is provided by the server.

    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.

    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """
    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue
        # print(response)
        # Display the transcription of the top alternative.
        transcripts = []
        for alternative in result.alternatives:
            transcripts.append((alternative.transcript.lower(),
                                alternative.confidence))
        transcripts.sort(key=lambda x: x[1], reverse=True)
        transcripts = list(map(lambda x: x[0], transcripts))
        return transcripts


def main():
    filename = 'hello.c'
    line = 5
    if len(sys.argv) == 3:
        filename = sys.argv[1]
        line = int(sys.argv[2])

    os.environ.update({'GOOGLE_APPLICATION_CREDENTIALS':
                       '/Users/himanshusonthalia/Desktop/ProjectCodac/credentials.json'})
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    language_code = 'en-US'  # a BCP-47 language tag

    client = speech.SpeechClient()
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,
        max_alternatives=3,
        speech_contexts=[speech.types.SpeechContext(
            phrases=[
                # keywords
                'add', 'declare', 'include', 'stdio', 'function', 'array',
                'return', 'go', 'goto', 'go to', 'paste', 'compile', 'execute',
                'loop', 'variable', 'move to', 'loop variable',
                # variable names
                'a', 'b', 'c', 'i', 'j', 'k', 'x', 'y', 'z', 'found', 'main',
                'function main', 'function called main', 'variable i',
                # helplessness
                'condition i less', 'array a at', 'modulus d'
            ],
        )],
        model='command_and_search',
    )
    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        single_utterance=True,
    )

    print(json.dumps({'status': 'ready'}))
    sys.stdout.flush()

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        transcripts = listen_print_loop(responses)
        for i in range(len(transcripts)):
            transcripts[i] = transcripts[i].replace('=', 'equals')
        action = get_action(transcripts, filename, line)
        print(action)
        sys.stdout.flush()

if __name__ == '__main__':
    main()
