import numpy as np
import librosa
import librosa.display

#y, sr = librosa.load("Gangnam Style.ogg")

n_fft = 1024

lag = 2
n_mels = 138
fmin = 27.5
fmax = 16000.
max_size = 3


def standard_onset(filename):
    y, sr = librosa.load(filename)
    hop_length = int(librosa.time_to_samples(1. / 200, sr=sr))
    #S = librosa.feature.melspectrogram(y, sr=sr, n_fft=n_fft, hop_length=hop_length, fmin=fmin, fmax=fmax, n_mels=n_mels)
    #odf_default = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
    onset_default = librosa.onset.onset_detect(y=y, sr=sr, hop_length=hop_length, units='time')
    #onset_default2= librosa.onset.onset_detect(onset_envelope=odf_default, sr=sr, hop_length=hop_length, units='time')
    return (onset_default)

def superflux_onset(filename):
    y, sr = librosa.load(filename)
    hop_length = int(librosa.time_to_samples(1. / 200, sr=sr))
    S = librosa.feature.melspectrogram(y, sr=sr, n_fft=n_fft, hop_length=hop_length, fmin=fmin, fmax=fmax,n_mels=n_mels)
    odf_sf = librosa.onset.onset_strength(S=librosa.power_to_db(S, ref=np.max), sr=sr, hop_length=hop_length, lag=lag, max_size=max_size)
    onset_sf = librosa.onset.onset_detect(onset_envelope=odf_sf, sr=sr, hop_length=hop_length, units='time')
    return(onset_sf)

#onset_times = librosa.frames_to_time(onset_default)
