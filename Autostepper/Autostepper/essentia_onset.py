import essentia
import numpy as np
from essentia.standard import *


# Loading audio file
#audio = MonoLoader(filename='./Gangnam Style.ogg')()

# Phase 1: compute the onset detection function
# The OnsetDetection algorithm provides various onset detection functions. Let's use two of them.

def hfc_onset(filename):
    audio = MonoLoader(filename=filename)()
    od1 = OnsetDetection(method='hfc')
    w = Windowing(type='hann')
    fft = FFT()  # this gives us a complex FFT
    c2p = CartesianToPolar()  # and this turns it into a pair (magnitude, phase)
    pool = essentia.Pool()
    for frame in FrameGenerator(audio, frameSize=1024, hopSize=512):
        mag, phase, = c2p(fft(w(frame)))
        pool.add('features.hfc', od1(mag, phase))

    onsets = Onsets()
    onsets_hfc = onsets(essentia.array([pool['features.hfc']]), [1])
        # this algo expects a matrix, not a vector
        # you need to specify weights, but as there is only a single
        # function, it doesn't actually matter which weight you give it
    return (onsets_hfc)

def complex_onset(filename):
    audio = MonoLoader(filename=filename)()
    od2 = OnsetDetection(method='complex')
    w = Windowing(type='hann')
    fft = FFT()  # this gives us a complex FFT
    c2p = CartesianToPolar()  # and this turns it into a pair (magnitude, phase)
    pool = essentia.Pool()
    for frame in FrameGenerator(audio, frameSize=1024, hopSize=512):
        mag, phase, = c2p(fft(w(frame)))
        pool.add('features.complex', od2(mag, phase))
    onsets = Onsets()
    onsets_complex = onsets(essentia.array([pool['features.complex']]), [1])
    return (onsets_complex)

def complex_phase_onset(filename):
    audio = MonoLoader(filename=filename)()
    od2 = OnsetDetection(method='complex_phase')
    w = Windowing(type='hann')
    fft = FFT()  # this gives us a complex FFT
    c2p = CartesianToPolar()  # and this turns it into a pair (magnitude, phase)
    pool = essentia.Pool()
    for frame in FrameGenerator(audio, frameSize=1024, hopSize=512):
        mag, phase, = c2p(fft(w(frame)))
        pool.add('features.complex_phase', od2(mag, phase))
    onsets = Onsets()
    onsets_complex_phase = onsets(essentia.array([pool['features.complex_phase']]), [1])
    return (onsets_complex_phase)

def flux_onset(filename):
    audio = MonoLoader(filename=filename)()
    od2 = OnsetDetection(method='flux')
    w = Windowing(type='hann')
    fft = FFT()  # this gives us a complex FFT
    c2p = CartesianToPolar()  # and this turns it into a pair (magnitude, phase)
    pool = essentia.Pool()
    for frame in FrameGenerator(audio, frameSize=1024, hopSize=512):
        mag, phase, = c2p(fft(w(frame)))
        pool.add('features.flux', od2(mag, phase))
    onsets = Onsets()
    onsets_flux = onsets(essentia.array([pool['features.flux']]), [1])
    return (onsets_flux)

def melflux_onset(filename):
    audio = MonoLoader(filename=filename)()
    od2 = OnsetDetection(method='melflux')
    w = Windowing(type='hann')
    fft = FFT()  # this gives us a complex FFT
    c2p = CartesianToPolar()  # and this turns it into a pair (magnitude, phase)
    pool = essentia.Pool()
    for frame in FrameGenerator(audio, frameSize=1024, hopSize=512):
        mag, phase, = c2p(fft(w(frame)))
        pool.add('features.melflux', od2(mag, phase))
    onsets = Onsets()
    onsets_melflux = onsets(essentia.array([pool['features.melflux']]), [1])
    return (onsets_melflux)

def rms_onset(filename):
    audio = MonoLoader(filename=filename)()
    od2 = OnsetDetection(method='rms')
    w = Windowing(type='hann')
    fft = FFT()  # this gives us a complex FFT
    c2p = CartesianToPolar()  # and this turns it into a pair (magnitude, phase)
    pool = essentia.Pool()
    for frame in FrameGenerator(audio, frameSize=1024, hopSize=512):
        mag, phase, = c2p(fft(w(frame)))
        pool.add('features.rms', od2(mag, phase))
    onsets = Onsets()
    onsets_rms = onsets(essentia.array([pool['features.rms']]), [1])
    return (onsets_rms)

def infogain_onset(filename):
    audio = MonoLoader(filename=filename)()
    od1 = OnsetDetectionGlobal(method='infogain')

    onsets = Onsets()
    onset_matrix=od1(audio)
    onset_matrix=np.reshape(onset_matrix,(1, len(onset_matrix)))
    #print(onset_matrix.shape)
    weights=[]
    onsets_infogain = onsets(onset_matrix, [1])
        # this algo expects a matrix, not a vector
        # you need to specify weights, but as there is only a single
        # function, it doesn't actually matter which weight you give it
    return (onsets_infogain)

def beat_emphasis_onset(filename):
    audio = MonoLoader(filename=filename)()
    od1 = OnsetDetectionGlobal(method='beat_emphasis')

    onsets = Onsets()
    onset_matrix=od1(audio)
    onset_matrix=np.reshape(onset_matrix,(1, len(onset_matrix)))
    #print(onset_matrix.shape)
    weights=[]
    onsets_beat_emphasis = onsets(onset_matrix, [1])
        # this algo expects a matrix, not a vector
        # you need to specify weights, but as there is only a single
        # function, it doesn't actually matter which weight you give it
    return (onsets_beat_emphasis)

def mix_onset(filename):
    import sys
    audio = MonoLoader(filename=filename)()
    od2 = OnsetDetection(method='melflux')
    od1 = OnsetDetection(method='complex')
    w = Windowing(type='hann')
    fft = FFT()  # this gives us a complex FFT
    c2p = CartesianToPolar()  # and this turns it into a pair (magnitude, phase)
    pool = essentia.Pool()
    for frame in FrameGenerator(audio, frameSize=1024, hopSize=512):
        mag, phase, = c2p(fft(w(frame)))
        pool.add('features.melflux', od2(mag, phase))
        pool.add('features.complex', od1(mag, phase))
    onsets = Onsets()
    a=essentia.array([pool['features.melflux']])
    a=np.concatenate((a,essentia.array([pool['features.complex']])), axis=0)
    #print(a.shape)
    onsets_melflux = onsets(a, [0.5,0.5])
    #sys.exit()
    return (onsets_melflux)
