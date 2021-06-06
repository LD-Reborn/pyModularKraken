from __future__ import print_function
import os
from pocketsphinx import Pocketsphinx, get_model_path, get_data_path

model_path = get_model_path()
data_path = get_data_path()

config = {
'hmm': os.path.join(model_path, 'en-us'),
'lm': os.path.join(model_path, 'en-us.lm.bin'),
'dict': os.path.join(model_path, 'cmudict-en-us.dict')
}

ps = Pocketsphinx(**config)
ps.decode(
audio_file=os.path.join(data_path, 'goforward.raw'), # add your audio file here
buffer_size=2048,
no_search=False,
full_utt=False
)

print(ps.hypothesis())

#exit()
'''
import speech_recognition as sr     # import the library
 
r = sr.Recognizer()                 # initialize recognizer
with sr.Microphone() as source:     # mention source it will be either Microphone or audio files.
    print("Speak Anything :")
    audio = r.listen(source)        # listen to the source
    try:
        text = r.recognize_api(audio)    # use recognizer to convert our audio into text part.
        print("You said : {}".format(text))
    except:
        print("Sorry could not recognize your voice")    # In case of voice not recognized  clearly

#from pocketsphinx import LiveSpeech
#for phrase in LiveSpeech(): print(phrase)
'''