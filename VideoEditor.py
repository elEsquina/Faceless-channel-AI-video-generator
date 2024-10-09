import whisper
import os

os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"

import json
import random
import gc
from tqdm import tqdm
from moviepy.editor import (
    TextClip, CompositeVideoClip, AudioFileClip, VideoFileClip, concatenate_videoclips
)

class AudioProcessor:
    def __init__(self, audioPath, modelName="base.en"):
        self.audioPath = audioPath
        self.model = whisper.load_model(modelName)
        self.audio = AudioFileClip(self.audioPath)
        self.audioDuration = self.audio.duration


    def getWordTimestamps(self):
        if not os.path.isfile(self.audioPath):
            raise FileNotFoundError(f"The file at {self.audioPath} does not exist.")
        
        print("Transcribing Audio...")
        result = self.model.transcribe(self.audioPath, word_timestamps=True)
        
        if "segments" not in result:
            raise ValueError("Transcription result does not contain segments.")
        
        wordTimestamps = []
        with tqdm(total=len(result['segments']), desc="Extracting Word Timestamps") as pbar:
            for segment in result['segments']:
                for word in segment['words']:
                    wordTimestamps.append((word['word'], word['start'], word['end']))
                pbar.update(1)
        
        return wordTimestamps


    def close(self):
        self.audio.close()
        del self.audio
        del self.model
        gc.collect()


class VideoProcessor:
    def __init__(self, audioProcessor, backgroundVidFolder, outputVideoPath="wordByWordVideo.mp4", fontSize=100, fps=30, fontPath="libs/font.otf"):
        self.audioProcessor = audioProcessor
        self.backgroundVidFolder = backgroundVidFolder
        self.outputVideoPath = outputVideoPath
        self.fontSize = fontSize
        self.fps = fps
        self.fontPath = fontPath
        self.backgroundClip = None


    def processBackgroundVideos(self):
        videoFiles = [f for f in os.listdir(self.backgroundVidFolder) if f.endswith(('.mp4', '.mov', '.avi'))]
        if not videoFiles:
            raise FileNotFoundError("No video files found in the 'backgroundVidFolder' folder.")
        
        backgroundClips = []
        totalVideoDuration = 0
        
        while totalVideoDuration < self.audioProcessor.audioDuration:
            randomVideoFile = random.choice(videoFiles)
            videoPath = os.path.join(self.backgroundVidFolder, randomVideoFile)
            videoClip = VideoFileClip(videoPath)
            
            backgroundClips.append(videoClip)
            totalVideoDuration += videoClip.duration
        
        concatenatedBackground = concatenate_videoclips(backgroundClips).subclip(0, self.audioProcessor.audioDuration)
        del backgroundClips
        gc.collect()
        
        return concatenatedBackground


    def createTextClips(self, wordTimestamps):
        videoSize = self.backgroundClip.size
        textClips = []
        textSize = (720, 200)
        
        with tqdm(total=len(wordTimestamps), desc="Processing Text Clips") as pbar:
            for word, startTime, endTime in wordTimestamps:
                if startTime is not None and endTime is not None:
                    txtClip = TextClip(word, fontsize=self.fontSize, color='white', size=textSize, method='caption', font=self.fontPath, stroke_color='black', stroke_width=2)
                    txtClip = txtClip.set_start(startTime).set_end(endTime).set_pos('center')
                    textClips.append(txtClip)
                pbar.update(1)
        
        textClips = CompositeVideoClip(textClips, size=videoSize)
        gc.collect()
        return textClips


    def createVideo(self):
        wordTimestamps = self.audioProcessor.getWordTimestamps()
        self.backgroundClip = self.processBackgroundVideos()
        textClips = self.createTextClips(wordTimestamps)
        
        finalClip = CompositeVideoClip([self.backgroundClip, textClips.set_duration(self.audioProcessor.audioDuration)], size=self.backgroundClip.size)
        finalClip = finalClip.set_audio(self.audioProcessor.audio)

        finalClip.write_videofile(self.outputVideoPath, fps=self.fps, codec='h264_qsv', audio_codec='aac', threads=2)

        finalClip.close()
        self.backgroundClip.close()
        textClips.close()

        del textClips
        del self.backgroundClip
        gc.collect()



def ProcessObject(idx, dataObj):
    print(f"Processing video. {idx}")

    audioProcessor = AudioProcessor(audioPath=dataObj["audio"])
    videoProcessor = VideoProcessor(
        audioProcessor=audioProcessor,
        backgroundVidFolder="videos",
        outputVideoPath=f"out/{idx}.mp4",
    )
    videoProcessor.createVideo()
    
    audioProcessor.close()
    del audioProcessor
    del videoProcessor 

    gc.collect()
    print(f"Done processing video. {idx}")



with open("data.json", "r") as file:
    dataObj = json.load(file)

    for idx, obj in dataObj.items():
        if str(idx) == "0":
            continue
        if str(idx) == "10":
            continue

        ProcessObject(str(idx), obj)
