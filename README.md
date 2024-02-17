This application is designed to help with transcribing a research interview between a researcher and a single participant. 

It uses the vosk library for speaker disambiguation, and the openai whisper library for speech to text. 

To use: 
Install vosk and whisper

Downloas the vosk models:  
https://alphacephei.com/vosk/models

The first time you run, whisper will download it's own model.

Go to the constants file and set your whisper model size (https://github.com/openai/whisper)

Put your MP4 recording in input next to speakerStamps.txt 
Note: This application expects an MP4. You will have to edit main_convert.py if you want another format. 

Update speakerStamps.txt. 
speakerStamps.txt tags segments of your video for the system to use for speaker disambiguation. You can label each speaker as you wish (sample uses to Researcher and Participant). 
Tag a total of at least 30s of speech for each speaker.
To check if the system is pulling good audio, run main_convert.py, and check the speaker1.wav and speaker2.wav files. 

Run main.py. This will run all components of the pipeline. 

pipeline components can be run individually, respecting their dependencies. 

This can be useful if, say, there is a bug and one component crashes, you don't need to rerun the whole pipeline to carry onwards. Also if, say, you want to change the speaker tags, you can change the speakerStamps.txt, run main_convert, and run main_compile, without having to run the super long processes. 

main_compile_srt.py and main_compile_transcript.py are independant of eachother and depend on main_vosk_text_parsing.py (for the speaker data), main_vosk_speaker_sigs.py (for the speaker identification signatures), main_whisper.py (for the speech to text data), and main_convert.py (for the speaker tags). 

main_vosk_text_parsing.py, main_vosk_speaker_sigs.py, and main_whisper.py are independant of eachother and depend on main_convert for the audio file. main_vosk_speaker_sigs.py also depends on it for the speaker audio files. 



