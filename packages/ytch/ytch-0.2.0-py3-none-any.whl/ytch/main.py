import os
import streamlit as st
from ytch import metadata
from ytch.utils import (
    Client,
    YouTube,
    add_punctuation,
    download_yt_audio,
    transcribe,
    upload_gemini_audio,
    youtube_obj,
)

sess = st.session_state


def caption_ui(yt: YouTube | None, langs: list[str], api_key: str) -> None:
    st.markdown("#### 💬 &nbsp; Extract Captions")

    lang = st.selectbox(
        label="Select the language",
        key="caption-lang",
        options=langs,
        index=None,
        format_func=lambda x: x.split(".")[-1],
    )

    format = st.radio(
        label="Select the format",
        key="caption-format",
        options=["srt", "txt", "AI improved txt"],
        index=0,
        horizontal=True,
        disabled=not lang,
    )

    transcript = ""
    if lang:
        if format == "srt":
            transcript = yt.captions[lang].generate_srt_captions()
        elif format == "txt":
            transcript = yt.captions[lang].generate_txt_captions()
        else:
            raw_transcript = yt.captions[lang].generate_txt_captions()
            transcript = add_punctuation(api_key, raw_transcript)

    st.text_area(
        label="Captions",
        key="caption-output",
        value=transcript,
        height=400,
        disabled=not transcript,
    )


def transcribe_ui(yt: YouTube, api_key: str) -> str:
    """Streamlit UI for transcribing audio"""
    st.markdown("#### 🗣️ &nbsp; Transcribe Audio")
    with st.spinner("No captions found, transcribing audio with Gemini..."):
        client = Client(api_key=api_key)
        filename = yt.video_id.lower()
        buffer, mime_type = download_yt_audio(yt)
        audio_file = upload_gemini_audio(filename, buffer, mime_type, client)

        transcript = transcribe(audio_file, client)
        st.text_area(
            label="Transcript", key="transcript-output", value=transcript, height=400
        )


def confirm_transcribe(yt, api_key):
    st.info("No captions found, transcribing audio with Gemini?")
    if st.button("Confirm Transcribe", key="confirm-transcribe"):
        transcribe_ui(yt, api_key)


def body():
    with st.container(border=True, key="main-container"):
        api_key = st.text_input(
            label="Google API key",
            key="google-api-key",
            type="password",
            value=get_api_key("google"),
            help="Visit [Google](https://ai.google.dev/gemini-api/docs/api-key) to get the API key",
        )

        url = st.text_input("Youtube URL", key="url-input", disabled=not api_key)

        if not api_key or not url:
            st.stop()

        if not (yt := youtube_obj(url)):
            st.error("Invalid URL")
            st.stop()

        langs = [c.code for c in yt.captions]

        divider()

        if langs or not yt:
            caption_ui(yt, langs, api_key)
        else:
            confirm_transcribe(yt, api_key)


def app_header():
    icon_with_color = f":{metadata['color']}[:material/{metadata['icon']}:]"

    with st.container(key="app-header"):
        st.markdown(f"## {icon_with_color} &nbsp; {metadata['name']}")
        st.caption(metadata["description"])


def divider(key: int = 1):
    with st.container(key=f"divider{key}"):
        st.divider()


def get_api_key(brand: str) -> str | None:
    """Get API key from session state or environment variable otherwise return None"""
    key_name = f"{brand.upper()}_API_KEY"

    if key_name in sess:
        return sess[key_name]

    if value := os.environ.get(key_name):
        sess[key_name] = value
        return value
    return None


if __name__ == "__main__":
    app_header()
    body()
