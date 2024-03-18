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

from google.cloud import speech


# [START speech_transcribe_streaming]
def start_transcribing(itrator) -> speech.RecognitionConfig:
    """Streams transcription of the given audio file."""

    client = speech.SpeechClient()

    # [START speech_python_migration_streaming_request]
    # with open(stream_file, "rb") as audio_file:
    #     content = audio_file.read()

    # In practice, stream should be a generator yielding chunks of audio data.
    # stream = [content]

    requests = (
        speech.StreamingRecognizeRequest(audio_content=chunk) for chunk in itrator
    )

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
        sample_rate_hertz=48000,
        language_code="en-US",
    )

    streaming_config = speech.StreamingRecognitionConfig(config=config)

    # streaming_recognize returns a generator.
    # [START speech_python_migration_streaming_response]
    responses = client.streaming_recognize(
        config=streaming_config,
        requests=requests,
    )
    return responses
    # return responses
    # for response in responses:
    #     # Once the transcription has settled, the first result will contain the
    #     # is_final result. The other results will be for subsequent portions of
    #     # the audio.
    #     for result in response.results:
    #         print(f"Finished: {result.is_final}")
    #         print(f"Stability: {result.stability}")
    #         alternatives = result.alternatives
    #         # The alternatives are ordered from most likely to least.
    #         for alternative in alternatives:
    #             print(f"Confidence: {alternative.confidence}")
    #             print(f"Transcript: {alternative.transcript}")

    # [END speech_python_migration_streaming_response]
                
def main():
    # stream_file = "temp/audio_1710731386.webm"
    stream_file = "temp/audio_1710730314.webm"
    with open(stream_file, "rb") as audio_file:
        content = audio_file.read()

    # In practice, stream should be a generator yielding chunks of audio data.
    itrator = [content]
    # def chunk_generator():
    #     for content in itrator:
    #         yield content
            
    stream = start_transcribing(itrator)
    # Handle the response
    for response in stream:
        print(response.results)
    
if __name__ == "__main__":
    main()


