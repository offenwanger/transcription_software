import constants
import whisper
import csv
import time


def main():
    startTime = time.time()
    model = whisper.load_model(constants.MODEL_SIZE)
    transcript = model.transcribe(
        word_timestamps=True,
        audio=constants.FULL_AUDIO_FILE,
        verbose=False,
        language='en',
    )

    csvFile = open(constants.WHISPER_OUTPUT_FILE,
                   'w', encoding='utf-8',  newline='')
    csvWriter = csv.writer(csvFile)
    csvWriter.writerow(["Phrase Id", "Phrase start",
                       "Phrase End", "Word", "Word Start", "Probability"])

    for segment in transcript['segments']:
        if (segment['words']):
            for word in segment['words']:
                csvWriter.writerow(
                    [segment['id'], segment['start'], segment['end'], word['word'].strip(), word['start'], word['probability']])
    csvFile.close()

    print("completed in " + str(time.time() - startTime) + "seconds")


if __name__ == "__main__":
    main()
    print("done!")
