from async_streamingclient import RevAiAsyncStreamingClient
from rev_ai import MediaConfig
import asyncio


config = MediaConfig(content_type="audio/opus",layout="interleaved",rate=48000)

sc = RevAiAsyncStreamingClient(
    access_token="<token>",
    config=config)



async def main():
    stream_file = "output.opus"
    with open(stream_file, "rb") as audio_file:
        content = audio_file.read()
    
    # In practice, stream should be a generator yielding chunks of audio data.
    chunk_length = len(content) // 2
    stream = [
        content[start : start + chunk_length]
        for start in range(0, len(content), chunk_length)
    ]

    async def gen(stream):
        for chunk in stream:
            yield stream.pop(0)



    asy_itr = gen(stream)
    # itrator = [content[:1000]]
    # def chunk_generator():
    #     for content in itrator:
    #         yield content

    stream = await sc.start(asy_itr)
    # Handle the response
    async for response in stream:
        print(response)



    
if __name__ == "__main__":
    asyncio.run(main())