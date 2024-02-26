import main_compile_transcript
import main_compile_srt
import main_whisper
import main_vosk_text_parsing
import main_vosk_speaker_sigs
import main_convert
import time


startTime = time.time()

print('Converting MP4 and speaker timestamps to usable audio')
main_convert.main()
print('done')

print('Whisper speech to text... (this is slow)')
main_whisper.main()
print('done')

print("VOSKing for the speaker sigs")
main_vosk_speaker_sigs.main()
print('done')

print("VOSKing for the speaker stamps... (this is slow)")
main_vosk_text_parsing.main()
print('done')

print("compiling the transcript")
main_compile_transcript.main()
print('done!')

print("compiling the srt")
main_compile_srt.main()
print('done!')

print("completed in " + str(time.time() - startTime) + "seconds")