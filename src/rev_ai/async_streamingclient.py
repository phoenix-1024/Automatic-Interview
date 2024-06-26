# -*- coding: utf-8 -*-
"""StreamingClient tool used for streaming services"""

from websockets import client as ws_client
from websockets.exceptions import ConnectionClosedOK
# import threading
# import six
import json
import asyncio
# from . import __version__

__version__ = '2.19.4'

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


def on_error(error):
    raise error


def on_close(code, reason):
    print("Connection Closed. Code : {}; Reason : {}".format(code, reason))


def on_connected(job_id):
    print('Connected, Job ID : {}'.format(job_id))


class RevAiAsyncStreamingClient:
    def __init__(self,
                 access_token,
                 config,
                 version='v1',
                 on_error=on_error,
                 on_close=on_close,
                 on_connected=on_connected):
        """Constructor for Streaming Client
        :param access_token: access token which authorizes all requests and
            links them to your account. Generated on the settings page of your
            account dashboard on Rev AI.
        :param config: a MediaConfig object containing audio information.
            See MediaConfig.py for more information
        :param version (optional): version of the streaming api to be used
        :param on_error (optional): function to be called when receiving an
            error from the server
        :param on_close (optional): function to be called when the websocket
            closes
        :param on_connected (optional): function to be called when the websocket
            and thread starts successfully
        """
        if not access_token:
            raise ValueError('access_token must be provided')

        if not config:
            raise ValueError('config must be provided')

        self.access_token = access_token
        self.config = config
        self.base_url = 'wss://api.rev.ai/speechtotext/{}/stream'. \
            format(version)
        self.on_error = on_error
        self.on_close = on_close
        self.on_connected = on_connected
        

    async def start(self,
              generator,
              metadata=None,
              custom_vocabulary_id=None,
              filter_profanity=None,
              remove_disfluencies=None,
              delete_after_seconds=None,
              detailed_partials=None,
              start_ts=None,
              transcriber=None,
              language=None,
              skip_postprocessing=None):
        """Function to connect the websocket to the URL and start the response
            thread
        :param generator: generator object that yields binary audio data
        :param metadata: metadata to be attached to streaming job
        :param custom_vocabulary_id: id of custom vocabulary to be used with this streaming job
        :param filter_profanity: whether to mask profane words
        :param remove_disfluencies: whether to exclude filler words like "uh"
        :param delete_after_seconds: number of seconds after job completion when job is auto-deleted
        :param detailed_partials: whether to receive timestamps and confidence scores
        :param start_ts: number of seconds to offset all hypotheses timings
        :param transcriber: type of transcriber to use to transcribe the media file
        :param language: language to use for the streaming job
        :param skip_postprocessing: skip all text postprocessing on final hypotheses
        """
        url = self.base_url + '?' + urlencode({
            'access_token': self.access_token,
            'content_type': self.config.get_content_type_string(),
            'user_agent': 'RevAi-PythonSDK/{}'.format(__version__)
        })

        if custom_vocabulary_id:
            url += '&' + urlencode({'custom_vocabulary_id': custom_vocabulary_id})

        if metadata:
            url += '&' + urlencode({'metadata': metadata})

        if filter_profanity:
            url += '&' + urlencode({'filter_profanity': 'true'})

        if remove_disfluencies:
            url += '&' + urlencode({'remove_disfluencies': 'true'})

        if delete_after_seconds is not None:
            url += '&' + urlencode({'delete_after_seconds': delete_after_seconds})

        if detailed_partials:
            url += '&' + urlencode({'detailed_partials': 'true'})

        if start_ts:
            url += '&' + urlencode({'start_ts': start_ts})

        if transcriber:
            url += '&' + urlencode({'transcriber': transcriber})

        if language:
            url += '&' + urlencode({'language': language})

        if skip_postprocessing:
            url += '&' + urlencode({'skip_postprocessing': 'true'})

        try:
            self.client = await ws_client.connect(url)
        except Exception as e:
            self.on_error(e)

        self._start_send_data_thread(generator)

        return self._get_response_generator()

    async def end(self):
        """Function to end the streaming service, close the websocket.
        """
        await self.client.close()

    def _start_send_data_thread(self, generator):
        """Function to send binary audio data from a generator with threading
        :param generator: generator object that yields binary audio data
        """
        if not generator:
            raise ValueError('generator must be provided')
        asyncio.create_task(self._send_data(generator))
        

    async def _send_data(self, generator):
        """Function used in a thread to send requests to the server.
        :param generator: enumerator object that yields binary audio data
        """
        if not generator:
            raise ValueError('generator must be provided')

        async for chunk in generator:
            # print("sending chunk")
            await self.client.send(chunk)
    
        await self.client.send("EOS")

    async def _get_response_generator(self):
        """A generator of responses from the server. Yields the data decoded.
        """
        exit = False
        while not exit:
            try:
                data = await self.client.recv()
                data = json.loads(data)
                if data['type'] == 'connected':
                    self.on_connected(data['id'])
                else:
                    yield data
            except ConnectionClosedOK:
                print("ws connection closed")
                exit = True
