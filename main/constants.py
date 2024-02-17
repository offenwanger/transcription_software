import os
import sys

# Change this value to set the output folder name for your current transcription
RUN_TAG = "P2"
# whisper model size, recommend setting this to base for testing.
MODEL_SIZE = "large"

THIS_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))
OUTPUT_DIR = os.path.join(THIS_DIR, "output", 'transcription_'+RUN_TAG)

INPUT_DIR = os.path.join(THIS_DIR, "input")

MODEL_FOLDER = os.path.join(THIS_DIR, "model")
MODEL_SPK_FOLDER = os.path.join(THIS_DIR, "model-spk")

FULL_AUDIO_FILE = os.path.join(OUTPUT_DIR, 'fullaudio.wav')
SPEAKER1_FILE = os.path.join(OUTPUT_DIR, 'speaker1.wav')
SPEAKER2_FILE = os.path.join(OUTPUT_DIR, 'speaker2.wav')
SPEAKER1_SIG = os.path.join(OUTPUT_DIR, "speaker1sig.pickle")
SPEAKER2_SIG = os.path.join(OUTPUT_DIR, "speaker2sig.pickle")

SPEAKER_NAMES = os.path.join(OUTPUT_DIR, "speaker_names.pickle")

VOSK_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "vosk_data.csv")
WHISPER_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "whisper_data.csv")

HTML_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "transcript.html")
SRT_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "srt.html")
HTML_TEMPLATE_FILE = os.path.join(THIS_DIR, "index.html")
