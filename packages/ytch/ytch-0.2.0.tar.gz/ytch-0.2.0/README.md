# yt-ai

> Chat, Transcript, and Summarize YouTube Videos with AI

## Features

- extract captions from youtube videos
- transcribe youtube videos if captions are not available
- add punctuation and paragraphed the transcript
- chat with the transcript
- summarize the transcript

## Usage

- Run Directly with `uvx`

```bash
uvx yt-ai

# update with latest version
uvx yt-ai@latest
```

- Install Locally

```bash
uv tool install yt-ai

# then start the streamlit app
yt-ai
```

## API Keys

- api key fields in the app will be auto-filled after providing the `.env` file (optional)

```bash
uvx yt-ai path/to/your/.env
```

- content of `.env` file

```ini
GOOGLE_API_KEY=your-google-api-key
```

## Questions

- [Github issue]
- [LinkedIn]

[Github issue]: https://github.com/hoishing/yt-ai/issues
[LinkedIn]: https://www.linkedin.com/in/kng2
