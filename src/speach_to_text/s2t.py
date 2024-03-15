'''
speach to text using google
'''

from google.cloud import speech



def run_quickstart(stream_file) -> speech.RecognizeResponse:
    # Instantiates a client
    client = speech.SpeechClient()

    # The name of the audio file to transcribe
    with open(stream_file, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        language_code="en-US",
    )

    # Detects speech in the audio file
    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")
run_quickstart("/tmp/gradio/d8619433bb3f21d717330ad9370e30ee4f13c46e/audio.wav")