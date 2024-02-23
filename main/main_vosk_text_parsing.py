#!/usr/bin/env python3

import constants

from vosk import Model, KaldiRecognizer, SpkModel
import wave
import json
import os
import numpy as np
import time
import csv
from vosk import SetLogLevel
SetLogLevel(-1)


def main():
    startTime = time.time()

    if not os.path.exists(constants.MODEL_FOLDER):
        print("Model missing, {} not found. Please download the model from https://alphacephei.com/vosk/models and unpack as {}.".format(constants.MODEL_FOLDER))
        exit(1)
    if not os.path.exists(constants.MODEL_SPK_FOLDER):
        print("Speaker model missing, {} not found. Please download the speaker model from https://alphacephei.com/vosk/models and unpack.".format(constants.MODEL_SPK_FOLDER))
        exit(1)

    # now try to parse the file
    try:
        wf = wave.open(constants.FULL_AUDIO_FILE, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            print(constants.FULL_AUDIO_FILE + " is not the right format.")
            exit(1)

        model = Model(constants.MODEL_FOLDER)
        spk_model = SpkModel(constants.MODEL_SPK_FOLDER)
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetSpkModel(spk_model)
        rec.SetWords(True)

        csvFile = open(constants.VOSK_OUTPUT_FILE, 'w',
                       newline='', encoding='utf-8')
        csvWriter = csv.writer(csvFile)

        csvWriter.writerow(["Speaker Data", "Segment Timestamp",
                            "Segment Timestring", "Word", "Confidence", "Timestamp"])

        while True:
            data = wf.readframes(100)
            if len(data) == 0:
                break

            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                row = []

                if 'spk' in res:
                    row.append(res["spk"])
                else:
                    row.append('')

                timestamp, timetext = getStartTimestamp(res)
                row.append(timestamp)
                row.append(timetext)

                if ("result" in res):
                    for word in res["result"]:
                        rowCopy = list(row)
                        rowCopy.append(word["word"])
                        rowCopy.append(word["conf"])
                        rowCopy.append(word["start"])
                        csvWriter.writerow(rowCopy)
                csvFile.flush()

                print("Parsed "+timetext, end="\r")
        csvFile.close()
    except Exception as error:
        print("Error, failed to vosk file")
        print(error, __file__, error.__traceback__.tb_lineno)
        exit()

    print("completed in " + str(time.time() - startTime) + "seconds")


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


def getSpeaker(spk, spk1Sig, spk2Sig):
    if (spk1Sig.size == 0):
        print("Error, bad speaker1")
        return 0

    if (spk2Sig.size == 0):
        print("Error, bad speaker2")
        return 0

    dist1 = cosine_dist(spk1Sig, spk)
    dist2 = cosine_dist(spk2Sig, spk)
    return 0 if dist1 < dist2 else 1


def cosine_dist(x, y):
    nx = np.array(x)
    ny = np.array(y)
    return 1 - np.dot(nx, ny) / np.linalg.norm(nx) / np.linalg.norm(ny)


def getMillis(timestr):
    h, m, s = timestr.split(':')
    return (int(h) * 3600 + int(m) * 60 + int(s))*1000


def getStartTimestamp(res):
    if ("result" in res and len(res["result"]) > 0 and "start" in res["result"][0]):
        return res["result"][0]["start"], time.strftime('%H:%M:%S', time.gmtime(res["result"][0]["start"])),
    else:
        return 0, ""


if __name__ == "__main__":
    main()
    print("done!")
