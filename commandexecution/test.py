import sys, os
import pocketsphinx as ps
from pocketsphinx import Decoder
import sphinxbase
print(ps.get_model_path())
MODELDIR = ps.get_model_path()#"/usr/local/lib/python3.6/dist-packages/pocketsphinx/model"#/en-us"
config = Decoder.default_config()
#config.set_string('-hmm', os.path.join(MODELDIR, 'en-us/en-us'))
config.set_string('-hmm', os.path.join(MODELDIR, 'en-us'))
config.set_string('-allphone', os.path.join(MODELDIR, 'en-us/en-us-phone.lm.dmp'))
#config.set_string('-lm', os.path.join(MODELDIR, 'en-us/en-us.lm.bin'))
config.set_string('-lm', os.path.join(MODELDIR, 'en-us.lm.bin'))
#config.set_string('-dict', os.path.join(MODELDIR, 'en-us/cmudict-en-us.dict'))
config.set_string('-dict', os.path.join(MODELDIR, 'cmudict-en-us.dict'))
config.set_string('-logfn', '/dev/null')
decoder = Decoder(config)

import pyaudio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
stream.start_stream()

in_speech_bf = False
decoder.start_utt()
while True:
	buf = stream.read(1024)
	if buf:
		decoder.process_raw(buf, False, False)
		if decoder.get_in_speech() != in_speech_bf:
			in_speech_bf = decoder.get_in_speech()
			if not in_speech_bf:
				decoder.end_utt()
				print('hypResult:', decoder.hyp())
				print('Result:', decoder.hyp().hypstr)
				print ('Phonemes: ', [seg.word for seg in decoder.seg()])
				decoder.start_utt()
	else:
		break
decoder.end_utt()