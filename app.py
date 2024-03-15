import gradio as gr

from google.cloud import speech

class my_little_transcriber:

    def __init__(self,):
        self.text = ''

    def transcribe(self,stream_file) -> speech.RecognizeResponse:
        # Instantiates a client
        client = speech.SpeechClient()
        print(stream_file)
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
            self.text += " " + result.alternatives[0].transcript
        return self.text

t_c = my_little_transcriber()

demo = gr.Interface(
    t_c.transcribe,
    [ gr.Audio(format='wav', type='filepath', streaming=True)],
    [ "text"],
    live=True,
)

demo.launch()