from ytch import metadata

readme_md = """\
# {name}

> {description}

## Features

- extract captions from youtube videos
- transcribe youtube videos if captions are not available
- add punctuation and paragraphed the transcript
- chat with the transcript
- summarize the transcript

[youtube-icon]: https://api.iconify.design/bi:youtube.svg?color=%23ff4242
[screenshot-icon]: https://api.iconify.design/material-symbols:imagesmode-rounded.svg?color=%23ffae52

## Usage

- Run Directly with `uvx`

```bash
uvx {name}

# update with latest version
uvx {name}@latest
```

- Install Locally

```bash
uv tool install {name}

# then start the streamlit app
{name}
```

## API Keys

- api key fields in the app will be auto-filled after providing the `.env` file (optional)

```bash
uvx {name} path/to/your/.env
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
"""


if __name__ == "__main__":
    open("README.md", "w").write(
        readme_md.format(name=metadata["name"], description=metadata["description"])
    )
