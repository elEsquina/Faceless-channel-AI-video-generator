import os
from gc import collect
from json import load, dump
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
from TTS.api import TTS
from moviepy.editor import concatenate_audioclips, AudioFileClip

class myTTS:
    def __init__(self):
        self.tts_model = TTS(model_name="tts_models/en/ljspeech/vits", progress_bar=True, gpu=False)
    
    def __enter__(self):
        return self.tts_model
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.tts_model
        collect()


class Speaker:
    def __init__(self, tempDir, outputFile):
        self.audioFiles = []
        self.tempDir = tempDir
        self.outputFile = outputFile
    
    def generateFromTokens(self, sentences):
        for idx, sentence in enumerate(sentences):
            audio_path = os.path.join(self.tempDir, f"sentence_{idx}.wav")

            with myTTS() as tts_model:
                tts_model.tts_to_file(text=sentence, file_path=audio_path)
                self.audioFiles.append(audio_path)
            
            collect()
    
    def __enter__(self):
        return self 

    def __exit__(self, exc_type, exc_val, exc_tb):
        clips = [AudioFileClip(file) for file in self.audioFiles]
        final_clip = concatenate_audioclips(clips)
        final_clip.write_audiofile(self.outputFile)
        
        for clip in clips:
            clip.close()
        
        for file in self.audioFiles:
            try:
                os.remove(file)
            except OSError as e:
                print(f"Error removing file {file}: {e}")

        collect()


with open("data.json", "r") as file: 
    dataobject = load(file)

    for idx, obj in dataobject.items():
        if obj["audio"] is None:
            outputFile="audios/{}.wav".format(idx)

            with Speaker("TEMP", outputFile) as speaker:
                speaker.generateFromTokens(obj["tokens"])
    
            obj["audio"] = outputFile
            with open("data.json", "w+") as filey:
                dump(dataobject, filey)

            collect()
