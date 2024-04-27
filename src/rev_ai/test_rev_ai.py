from websockets import client as ws_client
from websockets.exceptions import ConnectionClosedOK
import asyncio


async def sender(ws,stream):
    for chunk in stream:
        print("sending chunk")
        await ws.send(chunk)
    
    await ws.send("EOS")

async def start_transcribing(stream):
    REVAI_ACCESS_TOKEN = "<token>"

    url = f"wss://api.rev.ai/speechtotext/v1/stream?access_token={REVAI_ACCESS_TOKEN}\
&content_type=audio/opus;\
layout=interleaved;\
rate=48000"

    
    async with ws_client.connect(url) as ws:
        try:
            stremer = asyncio.create_task(sender(ws,stream))
    
            
            while True:
                yield (await ws.recv()) 
            await asyncio.gather(stremer)
        except ConnectionClosedOK:
            print("ws connection closed")

async def main():
    stream_file = "output.opus"
    with open(stream_file, "rb") as audio_file:
        content = audio_file.read()
    
    # In practice, stream should be a generator yielding chunks of audio data.
    chunk_length = len(content) // 2
    stream = iter([
        content[start : start + chunk_length]
        for start in range(0, len(content), chunk_length)
    ])
    # itrator = [content[:1000]]
    # def chunk_generator():
    #     for content in itrator:
    #         yield content

    stream = start_transcribing(stream)
    # Handle the response
    async for response in stream:
        print(response)



    
if __name__ == "__main__":
    asyncio.run(main())
