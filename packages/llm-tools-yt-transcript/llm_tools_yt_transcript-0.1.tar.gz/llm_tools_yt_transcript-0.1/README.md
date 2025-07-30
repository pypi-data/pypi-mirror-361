# llm-tools-yt-transcript

[![PyPI](https://img.shields.io/pypi/v/llm-tools-yt-transcript.svg)](https://pypi.org/project/llm-tools-yt-transcript/)
[![Changelog](https://img.shields.io/github/v/release/rupello/llm-tools-yt-transcript?include_prereleases&label=changelog)](https://github.com/rupello/llm-tools-yt-transcript/releases)
[![Tests](https://github.com/rupello/llm-tools-yt-transcript/actions/workflows/test.yml/badge.svg)](https://github.com/rupello/llm-tools-yt-transcript/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/rupello/llm-tools-yt-transcript/blob/main/LICENSE)

Makes YouTube transcripts available to [LLM](https://llm.datasette.io/)

This is useful for generating a quick overview of a YouTube video before deciding to watch it

Note: this uses [the youtube-transcript-api library](https://pypi.org/project/youtube-transcript-api/) with this caveat:

    This code uses an undocumented part of the YouTube API, which is called by the YouTube web-client. So there is no guarantee that it won't stop working tomorrow, if they change how things work. I will however do my best to make things working again as soon as possible if that happens. So if it stops working, let me know!

## Installation

Install this plugin in the same environment as [LLM](https://llm.datasette.io/).
```bash
llm install llm-tools-yt-transcript
```
## Usage

To use this with the [LLM command-line tool](https://llm.datasette.io/en/stable/usage.html):

```bash

# basic example
llm --tool yt_transcript "summarize this video: https://www.youtube.com/watch?v=kaMKInkV7Vs"  --tools-debug

# a more sophisticated report
cat yt-digest-prompt-template.txt | llm --save yt-digest
llm -t yt-digest "https://www.youtube.com/watch?v=kaMKInkV7Vs" -T yt_transcript -x > example-report.html

```

With the [LLM Python API](https://llm.datasette.io/en/stable/python-api.html):

```python
import llm
from llm_tools_yt_transcript import yt_transcript

model = llm.get_model("gpt-4.1-mini")

result = model.chain(
    "Example prompt goes here",
    tools=[yt_transcript]
).text()
```

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:
```bash
cd llm-tools-yt-transcript
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
llm install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
