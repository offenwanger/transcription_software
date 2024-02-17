import os
from moviepy.editor import *
from pydub import AudioSegment
import pickle

import constants


def main():
    files = os.listdir(constants.INPUT_DIR)
    for speakerFile in files:
        if speakerFile.endswith(".txt"):
            break
    else:
        speakerFile = None

    for mp4File in files:
        if mp4File.endswith(".mp4"):
            break
    else:
        mp4File = None

    if speakerFile == None or mp4File == None:
        print("Files missing, found " + repr(speakerFile) +
              " for speaker file and " + repr(mp4File) + " for the mp4 file")
        exit(1)

    speakerFile = os.path.join(constants.INPUT_DIR, speakerFile)
    mp4File = os.path.join(constants.INPUT_DIR, mp4File)
    if not os.path.exists(constants.OUTPUT_DIR):
        os.makedirs(constants.OUTPUT_DIR)

    # First conver the mp4 to the correct wav file
    try:
        audioFile = os.path.join(constants.OUTPUT_DIR, 'fullaudio.mp3')
        video = VideoFileClip(mp4File)
        audio = video.audio
        audio.write_audiofile(audioFile)

        audio = AudioSegment.from_mp3(audioFile)
        # Convert to mono
        audio = audio.set_channels(1)
        # Set frame rate
        audio = audio.set_frame_rate(16000)
        audio.export(constants.FULL_AUDIO_FILE, format="wav")
    except Exception as error:
        print("Error, failed to create the audio file from the video file")
        print(error, __file__, error.__traceback__.tb_lineno)
        exit(1)

    # then parse the speaker files
    try:
        file = open(speakerFile, "r")
        speakerFileContent = file.readlines()
        speakerFileContent = list(
            filter(lambda a: len(a.strip()) > 0, speakerFileContent))
        s1name = None
        s2name = None
        s1segments = []
        s2segments = []
        for line in speakerFileContent:
            line = line.strip()
            if not ':' in line:
                if s1name == None:
                    s1name = line
                elif s2name == None:
                    s2name = line
                else:
                    break
            else:
                t1, t2 = line.split('-')
                if s2name == None:
                    s1segments.append(
                        [getMillis(t1.strip()), getMillis(t2.strip())])
                else:
                    s2segments.append(
                        [getMillis(t1.strip()), getMillis(t2.strip())])

        nameFile = open(constants.SPEAKER_NAMES, "wb")
        pickle.dump([s1name, s2name], nameFile)
        nameFile.close()

        if len(s2segments) == 0 or len(s1segments) == 0:
            print('Error, not enough speaker segments, speaker ' +
                  repr(s1name)+":"+len(s1segments)+", speaker "+s2name + ":"+len(s2segments))
        file.close()

        audio = AudioSegment.from_wav(constants.FULL_AUDIO_FILE)
        speaker1Audio = audio[0:1]
        for segment in s1segments:
            speaker1Audio = speaker1Audio+audio[segment[0]:segment[1]]
        speaker1Audio.export(constants.SPEAKER1_FILE, format="wav")
        speaker2Audio = audio[0:1]
        for segment in s2segments:
            speaker2Audio = speaker2Audio+audio[segment[0]:segment[1]]
        speaker2Audio.export(constants.SPEAKER2_FILE, format="wav")
    except Exception as error:
        print("Error, failed to create the speaker audio files")
        print(error, __file__, error.__traceback__.tb_lineno)
        exit(1)


def getMillis(timestr):
    h, m, s = timestr.split(':')
    return (int(h) * 3600 + int(m) * 60 + int(s))*1000


if __name__ == "__main__":
    main()
    print("done!")
