#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer, SpkModel
import sys
import wave
import json
import os
import numpy as np
import time
import shutil

from vosk import SetLogLevel
SetLogLevel(-1)

thisDir = os.path.abspath(os.path.dirname(sys.argv[0]))

####    PARAMETERS  ####
# Speak 1 and speaker 2 are WAVs that contain only the two speakers
# The are used to create features to disambiguate the two speakers

speaker1_filePath = os.path.join(thisDir, "speaker1.wav")
speaker2_filePath = os.path.join(thisDir, "speaker2.wav")

# Full recording is of course the full recording, and it will be output into an html file
recording_filePath = os.path.join(thisDir, "full_recording.wav")
outfile_filePath = os.path.join(thisDir, "transcription.html")

########################

indexHtml_path = os.path.join(thisDir, "index.html")
model_path = os.path.join(thisDir, "model")
spk_model_path = os.path.join(thisDir, "model-spk")

if not os.path.exists(model_path):
    print ("Model missing, {} not found. Please download the model from https://alphacephei.com/vosk/models and unpack as {}.".format(model_path))
    exit (1)

if not os.path.exists(spk_model_path):
    print ("Speaker model missing, {} not found. Please download the speaker model from https://alphacephei.com/vosk/models and unpack.".format(spk_model_path))
    exit (1)

def getSpeakerSig(filePath):
    wf = wave.open(filePath, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print (filePath + " Audio file must be WAV format mono PCM.")
        exit (1)

    # Large vocabulary free form recognition
    model = Model(model_path)
    spk_model = SpkModel(spk_model_path)
    #rec = KaldiRecognizer(model, wf.getframerate(), spk_model)
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

    return np.mean(spk_sig, 0)

def getSpeaker(spk, spk1Sig, spk2Sig):
    dist1 = cosine_dist(spk1Sig, spk)
    dist2 = cosine_dist(spk2Sig, spk)
    return 0 if dist1 < dist2 else 1

def cosine_dist(x, y):
    nx = np.array(x)
    ny = np.array(y)
    return 1 - np.dot(nx, ny) / np.linalg.norm(nx) / np.linalg.norm(ny)

def parseText(inFile, outFileName, speaker1, speaker2):
    wf = wave.open(inFile, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print (inFile + " Audio file must be WAV format mono PCM.")
        exit (1)

    model = Model(model_path)
    spk_model = SpkModel(spk_model_path)
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetSpkModel(spk_model)
    rec.SetWords(True)

    if os.path.exists(outFileName):
        os.remove(outFileName)
    shutil.copyfile(indexHtml_path, outFileName)    

    file_object = open(outFileName, 'a')
    file_object.write("<audio id = 'audioPlayer' controls src='"+ os.path.basename(inFile) +"'> Your browser does not support the <code>audio</code> element. </audio></div>")
    file_object.write("<div class='main' id='fake_textarea' contenteditable>")
    file_object.write("<p>")
    file_object.close()

    lastspeaker = -1
    lastTime = 0
    while True:
        data = wf.readframes(500)
        if len(data) == 0:
            break
        
        file_object = open(outFileName, 'a')

        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())

            if 'spk' in res:
                speaker = getSpeaker(res["spk"], speaker1, speaker2)
                if(lastspeaker != speaker):
                    lastspeaker = speaker
                    file_object.write("</p><p>")

                    timestamp, timetext = getStartTimestamp(res)
                    if(timestamp - lastTime > 60):
                        file_object.write(timetext + "<br>")
                        lastTime = timestamp

                    file_object.write(str(speaker) + ": ")

            if("result" in res):
                for word in res["result"]:
                    file_object.write(tagWord(word["word"], word["conf"], word["start"]) + " ")

        file_object.close()

    file_object = open(outFileName, 'a')
    file_object.write("</div>")
    file_object.close()

def tagWord(text, conf, time):
    if(conf < 0.5):
        conf = 0.5

    spanTag = "<span onclick='wordOnClick("+str(time)+")' "

    # if conf is less than one, add color. 
    if(conf < 1.0):
        spanTag = spanTag + "style='background-color:rgb(255, "+str(2*(conf - 0.5) * 255)+", "+str(2*(conf - 0.5) * 255)+")'"

    return spanTag + ">" + text + "</span>"

def getStartTimestamp(res):
    if("result" in res and len(res["result"]) > 0 and "start" in res["result"][0]):
        return res["result"][0]["start"], time.strftime('%H:%M:%S', time.gmtime(res["result"][0]["start"])), 
    else:
        return 0, ""

print("calculating speaker 1")
sig1 = getSpeakerSig(speaker1_filePath)
print("calculating speaker 2")
sig2 = getSpeakerSig(speaker2_filePath)

print("parsing text")
parseText(recording_filePath, outfile_filePath, sig1, sig2)

print("done!")