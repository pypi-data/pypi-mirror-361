import tomllib
from pathlib import Path


def pyproject_data() -> dict:
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    with pyproject_path.open("rb") as f:
        return tomllib.load(f)


metadata = pyproject_data()["project"]

metadata |= {
    "icon": "youtube_activity",
    "color": "red",
    "youtube": "https://youtu.be/BdSL8LLJOok, https://youtu.be/I5r0O7iMjKc",
}
