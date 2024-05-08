# Copyright 2017 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Cloud Speech API sample application using the streaming API.

Example usage:
    python transcribe_streaming.py resources/audio.raw
"""

import queue

from rev_ai.models import MediaConfig
from rev_ai.streamingclient import RevAiStreamingClient


async def start_transcribing(a_itrator):
    # Create a client
    client = speech_v1.SpeechAsyncClient()
    
    # Initialize request argument(s)
    streaming_config = speech_v1.StreamingRecognitionConfig()
    streaming_config.config.language_code = "en-US"
    streaming_config.config.encoding = speech.RecognitionConfig.AudioEncoding.WEBM_OPUS
    streaming_config.config.sample_rate_hertz = 48000

    s_config = speech_v1.StreamingRecognizeRequest(
        streaming_config=streaming_config,
    )

    # This method expects an iterator which contains
    # 'speech_v1.StreamingRecognizeRequest' objects
    # requests (AsyncIterator[`google.cloud.speech_v1.types.StreamingRecognizeRequest`]):
    # The request object AsyncIterator. The top-level message sent by the client for the
    # ``StreamingRecognize`` method. Multiple
    # ``StreamingRecognizeRequest`` messages are sent. The
    # first message must contain a ``streaming_config``
    # message and must not contain ``audio_content``. All
    # subsequent messages must contain ``audio_content`` and
    # must not contain a ``streaming_config`` message.

    async def request_generator(s_config, a_itrator):
        yield s_config
        print("sending chunks of config")
        async for chunk in a_itrator:
            print("sending chunks of audio")
            # yield audio_content
            yield speech_v1.StreamingRecognizeRequest(audio_content=chunk)

    # Make the request
    stream = await client.streaming_recognize(requests=request_generator(s_config,a_itrator))
    
    return stream

async def main():
    stream_file = "temp/audio_1710731386.webm"
    with open(stream_file, "rb") as audio_file:
        content = audio_file.read()
    
    # In practice, stream should be a generator yielding chunks of audio data.
    chunk_length = len(content) // 2
    stream = [
        content[start : start + chunk_length]
        for start in range(0, len(content), chunk_length)
    ]
    # itrator = [content[:1000]]
    # def chunk_generator():
    #     for content in itrator:
    #         yield content

    stream = await start_transcribing(stream)
    # Handle the response
    async for response in stream:
        print(response.results)
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


