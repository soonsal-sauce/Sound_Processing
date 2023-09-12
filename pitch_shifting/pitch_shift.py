'''
   This method is based on SingAug[S.Guo et al., 2022] pitch shifting method
-> By applying this method, -2 ~ 2 semitone modification doesn't harm formants of .wavfile
-> But sometimes, if the given .wav file has lots of reverberaton and accumulated chorous, then the shifting will not be done as expected.
'''

import os
import pyworld as pw
import scipy
from scipy.io import wavfile
from scipy.io.wavfile import write, read
import numpy as np
import soundfile as sf
from tqdm import tqdm

#hyperparameters - what ever you want except for the twelfth_root
'''
+ : up shifting
- : down shifting
0 : no shifting
'''
semitone_list=[-3, -2, -1, 0, 1, 2, 3]
twelfth_root = 1.059
wav_path = 'Source wave path'

def pitch_shift(semitone, f0):
    new_f0 = 1
    if semitone > 0: # Positive integer (Up)
        for i in range(semitone):
            if i == 0:
                new_f0 = f0 * twelfth_root
            else:
                new_f0 = prev * twelfth_root
            prev = new_f0

    else:            # Negative integer (Down)
        for i in range(abs(semitone)):
            if i == 0:
                new_f0 = f0 / twelfth_root
            else:
                new_f0 = prev / twelfth_root
            prev = new_f0
    return new_f0




for song in tqdm(os.listdir(wav_path)):
    if song.endswith(".wav"):
        sn = song
        sr, song  = wavfile.read(wav_path+song)
        song = song.astype(np.float64)
        _f0, t = pw.dio(song, sr)
        f0 = pw.stonemask(song, _f0, t, sr)
        sp = pw.cheaptrick(song, f0, t, sr)
        ap = pw.d4c(song, f0, t, sr)
    

        for s in tqdm(semitone_list):
            new_sn = sn.replace(".wav", "_") + str(s) + "_shifted"
           
            if s == 0:
                new_f0 = f0
            else:   
                new_f0 = pitch_shift(s, f0)
                
            #Generate waveform
            y = pw.synthesize(new_f0, sp, ap, sr)

            #Sound volume adjustment(Normalizing)
            y = np.int16(y/np.max(np.abs(y)) * 32767) 
            #Save waveform
            sf.write(f'Result Saving Path_{new_sn}.wav', y, sr)
