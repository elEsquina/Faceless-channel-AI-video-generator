# Faceless channel AI video generator that I will call TrendifyAI

TrendifyAI is an AI-powered tool that automates the process of creating engaging, trendy videos for social media. By leveraging content scraping, advanced audio processing, and dynamic video editing, TrendifyAI transforms Reddit posts into visually appealing videos styled after Instagram trends.

## Features

- **Reddit Scraper**: Automatically scrapes and sanitizes posts from multiple Reddit subreddits, ensuring the content is clean and relevant.
- **Text-to-Speech Conversion**: Utilizes state-of-the-art AI voice synthesis to convert text from Reddit posts into natural-sounding speech, with precise word-by-word timestamps for synchronization.
- **Video Creation**: Edits and composes videos with dynamic text overlays that appear word by word, creating an engaging viewing experience.

## Components

### 1. Reddit Scraper
The **Scrapper** class fetches posts from specified subreddits, sanitizes them, and saves the output in a structured JSON format.

**Key Methods:**
- `scrape_subreddit`: Fetches posts from a specific subreddit.
- `sanitize_posts`: Cleans up the post text for better readability.
- `tokenize_post`: Splits posts into sentences for speech synthesis.
- `save`: Saves the sanitized posts and their tokens to `data.json`.

### 2. Text-to-Speech Conversion
The **Speaker** class generates audio files from the tokenized sentences of Reddit posts.

**Key Methods:**
- `generateFromTokens`: Converts each sentence into audio files using the TTS API.
- Audio files are saved temporarily and combined into a single output file.

### 3. Video Processor
The **VideoProcessor** class composes the final video by synchronizing the generated audio with background video clips.

**Key Methods:**
- `processBackgroundVideos`: Selects and concatenates background video clips based on the duration of the audio.
- `createTextClips`: Creates text overlays that match the timing of the audio.
- `createVideo`: Assembles the final video from the background clips and text overlays.

## Getting Started

### Prerequisites

- Python 3.8+
- `pip` package manager
- Required libraries: `BeautifulSoup`, `requests`, `nltk`, `moviepy`, `TTS`, `tqdm`, `whisper` (install via `pip install -r requirements.txt`).

### Installation

1. Clone the repository:
   ```bash
    git clone https://github.com/elEsquina/Faceless-channel-AI-video-generator.git
    cd trendifyai
    ``` 