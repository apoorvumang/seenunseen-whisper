# Seen Unseen transcripts
Transcriptions of the [seenunseen.in](https://seenunseen.in/) podcast by Amit Varma. `Note:` All transcription and speaker tagging were done automatically and may contain errors.

These transcriptions can also be browsed on https://apoorvumang.github.io/seenunseen/

## Method

1. Audio data was scraped from seenunseen.in. Total data amounted to approximately 692 hours of audio (till episode 310).
2. Raw transcripts (without speaker annotation) for the podcast were generated using [OpenAI's whisper model](https://github.com/openai/whisper). `whisper large-v2` model was used, with default settings (auto identify language, since some podcasts like EP86 are in Hindi)
3. Speaker diarization was done using [pyannote](https://github.com/pyannote/pyannote-audio). Speakers with less than 10% of total speaking time were set to UNKNOWN (in order to remove speakers that are neither Amit nor a guest, eg. the lady that says 'I.V.M').
4. Diarization and transcription output was combined to make a single subtitle file. This was done using matching at a 'seconds' level. Note: this resulted in less than perfect diarization since the chunking done by whisper is very coarse, and often a single chunk contains dialogues from multiple speakers. This output is available in folder [transcripts_vtt/](/transcripts_vtt). (heuristics were used to identify which speaker is Amit Varma).
5. Subtitle-style output was further processed to create the chat-like output available in folder [transcripts_chat/](/transcripts_chat)
6. A generative model (flan-t5-xl) was used to generate headings for parts of the transcripts. This was done for easier navigation/browsing of extremely long transcripts. These can be found in folder [flant5_titles/](/flant5_titles)

## Data format

`metadata.json` contains metadata like
```
[
    {
        "epnum": 1,
        "title": "Episode 1: Entry and Exit in Agriculture",
        "url": "https://seenunseen.in/episodes/2017/1/16/episode-1-entry-and-exit-in-agriculture/",
        "description": "India has a panoply of ...",
        "date_published": "16 Jan 2017"
    },
    ...
]
```

`transcripts_vtt` has a vtt file for each episode. Each line contains maximum of 30 seconds of audio, and is tagged with speaker name (Amit Varma or Guest)
```
00:00:00.000 --> 00:00:07.000
[Guest 2]: Welcome to the IBM Podcast Network.

00:00:07.000 --> 00:00:20.000
[Amit Varma]: Ram Singh is a farmer in a small village in India. One morning he woke up to a loud noise coming from over his head....

...
```

`transcripts_chat` has a json file for each episode. Each json file is a list of 'chat messages' containing speaker, start time and message.
```
[
    {
        "speaker": "Guest 2",
        "time": "00:00:00.000",
        "message": "Welcome to the IBM Podcast Network."
    },
    {
        "speaker": "Amit Varma",
        "time": "00:00:07.000",
        "message": "Ram Singh is a farmer in ..."
    },
    ...
]
```

`flant5_titles` has a json file for each episode. Each json file is a list of 'section titles' containing title (machine generated), time and a title log-likelihood (higher the better).
```
[
    {
        "title": "The story of agriculture in India",
        "time": "00:00:07.000",
        "title_prob": -0.8173360824584961
    },
    ...
]
```

## Transcribing a new episode

Please follow [`run_pipeline_new_episode.ipynb`](run_pipeline_new_episode.ipynb) to run the pipeline on a new episode (downloading audio, running transcription and diarization, and then combining to single file). The code will not execute directly but should provide a good reference.

You will need a pytorch installation, along with the following stuff to run the pipeline
```
sudo apt install ffmpeg
pip install git+https://github.com/openai/whisper.git
pip install pyvtt
pip install pyannote.audio
```
