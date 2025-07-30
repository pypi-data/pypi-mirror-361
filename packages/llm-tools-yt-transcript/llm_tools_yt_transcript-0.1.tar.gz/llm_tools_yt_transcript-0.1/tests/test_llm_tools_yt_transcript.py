import llm
import json
import pytest
from llm_tools_yt_transcript import yt_transcript


@pytest.mark.skip("requires internet access")
def test_tool():
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps(
            {
                "tool_calls": [
                    {"name": "yt_transcript", "arguments": {"input": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}}
                ]
            }
        ),
        tools=[yt_transcript],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]

    # asserts
    assert tool_results[0]['name'] == 'yt_transcript'
    video_data = json.loads(tool_results[0]['output'])
    assert set(video_data.keys()) == {'title', 'version', 'height', 'transcript', 'thumbnail_url', 'author_name', 'thumbnail_height', 'thumbnail_width', 'width', 'type', 'html', 'provider_url', 'author_url', 'provider_name'}

