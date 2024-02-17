#!/usr/bin/env python3
import constants
import os
import csv
import ast
import pickle
import numpy as np
import shutil
import time


def main():
    voskFile = open(constants.VOSK_OUTPUT_FILE, 'r', encoding='utf-8')
    voskReader = csv.reader(voskFile)
    whisperFile = open(constants.WHISPER_OUTPUT_FILE, 'r', encoding='utf-8')
    whisperReader = csv.reader(whisperFile)
    speaker1File = open(constants.SPEAKER1_SIG, 'rb')
    speaker1 = pickle.load(speaker1File)
    speaker1File.close()
    speaker2File = open(constants.SPEAKER2_SIG, 'rb')
    speaker2 = pickle.load(speaker2File)
    speaker2File.close()
    speakerNamesFile = open(constants.SPEAKER_NAMES, 'rb')
    speakerNames = pickle.load(speakerNamesFile)
    speakerNamesFile.close()

    shutil.copyfile(constants.HTML_TEMPLATE_FILE, constants.HTML_OUTPUT_FILE)
    file_object = open(constants.HTML_OUTPUT_FILE, 'a', encoding='utf-8')

    file_object.write("<audio id = 'audioPlayer' controls src='" + os.path.basename(constants.FULL_AUDIO_FILE) +
                      "'> Your browser does not support the <code>audio</code> element. </audio></div>")
    file_object.write("<div class='main' id='fake_textarea' contenteditable>")
    file_object.write("<p>")

    speakerData = []
    lastTimeStamp = -1
    for row in voskReader:
        if (row[0] == "Speaker Data"):
            continue

        if(len(row[0]) == 0):
            continue
        
        speakersig = ast.literal_eval(row[0])
        speakersig = map(lambda x: float(x), speakersig)
        speakersig = list(speakersig)
        speaker = getSpeaker(speakersig, speaker1, speaker2)
        timestamp = float(row[1])

        if lastTimeStamp != timestamp:
            speakerData.append([timestamp, speaker])
            lastTimeStamp = timestamp

    speakerIndex = 0
    lastTime = 0

    for row in whisperReader:
        if (row[0] == "Phrase Id"):
            continue

        word = row[3]
        timestamp = float(row[4])
        certainty = float(row[5])

        newSpeaker = False
        if len(speakerData) > (speakerIndex + 1) and speakerData[speakerIndex + 1][0] < timestamp:
            speakerIndex = speakerIndex + 1
            if speakerData[speakerIndex][1] != speakerData[speakerIndex-1][1]:
                newSpeaker = True

        if timestamp - lastTime > 60 or newSpeaker:
            lastTime = timestamp
            file_object.write("</p><p>")
            timetext = time.strftime('%H:%M:%S', time.gmtime(timestamp))
            file_object.write(timetext + "<br>")

        if newSpeaker:
            file_object.write(
                speakerNames[speakerData[speakerIndex][1]] + ": ")

        file_object.write(tagWord(word, certainty, timestamp) + " ")

    file_object.write("</div>")
    file_object.close()


def tagWord(text, conf, time):
    if (conf < 0.5):
        conf = 0.5

    spanTag = "<span onclick='wordOnClick("+str(time)+")' "

    # if conf is less than one, add color.
    if (conf < 1.0):
        spanTag = spanTag + "style='background-color:rgb(255, "+str(
            2*(conf - 0.5) * 255)+", "+str(2*(conf - 0.5) * 255)+")'"

    return spanTag + ">" + text + "</span>"


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


if __name__ == "__main__":
    main()
    print("done!")
