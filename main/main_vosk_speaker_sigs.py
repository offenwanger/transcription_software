#!/usr/bin/env python3

import constants

from vosk import Model, KaldiRecognizer, SpkModel
import wave
import json
import os
import numpy as np
import time
import csv
import pickle
from vosk import SetLogLevel
SetLogLevel(-1)


def main():
    if not os.path.exists(constants.MODEL_FOLDER):
        print("Model missing, {} not found. Please download the model from https://alphacephei.com/vosk/models and unpack as {}.".format(constants.MODEL_FOLDER))
        exit(1)
    if not os.path.exists(constants.MODEL_SPK_FOLDER):
        print("Speaker model missing, {} not found. Please download the speaker model from https://alphacephei.com/vosk/models and unpack.".format(constants.MODEL_SPK_FOLDER))
        exit(1)

    try:
        print("calculating speaker 1")
        speaker1 = getSpeakerSig(constants.SPEAKER1_FILE)
        sig1File = open(constants.SPEAKER1_SIG, "wb")
        pickle.dump(speaker1, sig1File)
        sig1File.close()

        print("calculating speaker 2")
        speaker2 = getSpeakerSig(constants.SPEAKER2_FILE)
        sig2File = open(constants.SPEAKER2_SIG, "wb")
        pickle.dump(speaker2, sig2File)
        sig2File.close()

    except Exception as error:
        print("Error, failed to create the speaker audio files")
        print(error, __file__, error.__traceback__.tb_lineno)
        exit()


def getSpeakerSig(filePath):
    wf = wave.open(filePath, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print(filePath + " Audio file must be WAV format mono PCM.")
        exit(1)

    # Large vocabulary free form recognition
    model = Model(constants.MODEL_FOLDER)
    spk_model = SpkModel(constants.MODEL_SPK_FOLDER)
    # rec = KaldiRecognizer(model, wf.getframerate(), spk_model)
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetSpkModel(spk_model)

    # We compare speakers with cosine distance. We can keep one or several fingerprints for the speaker in a database
    # to distingusih among users.
    spk_sig = []

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())

            if 'spk' in res:
                spk_sig.append(res['spk'])

    if (len(spk_sig) == 0):
        print("Error! vosk did not accept speaker text")
        print("Increasing the quantity of audio can help (min 20s is advised)")
        return np.array([])

    return np.mean(spk_sig, 0)


if __name__ == "__main__":
    main()
    print("done!")
