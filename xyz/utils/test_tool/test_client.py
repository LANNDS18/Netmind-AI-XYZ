"""
============
TestClient
============
@file_name: test_client.py
@description:
This is a dummy LLM-CLient. It will not do an request. But it can check the request and response for openai API.

## Initialization
Users initialize the OpenAIClient by specifying the api_key and generate_args:

- `api_key`: The API key for OpenAI. This must be obtained from your OpenAI account.
- `generate_args`: Arguments for the chat completion request. For detailed information on these parameters, refer to the
 OpenAI documentation. https://platform.openai.com/docs/api-reference/chat/create

## Methods
The class includes two primary methods for interacting with OpenAI:

- `run`: This method is used to make standard requests to OpenAI. It accepts messages, images, and optionally tools as
parameters:
    - `messages`: A list of strings, each representing a conversation turn.
    - `images`: A list of URLs pointing to images to be included in the request.
    - `tools`: An optional list that specifies additional tools to be used in the request.
- `stream_run`: This method is designed for streaming requests to OpenAI and also requires the messages and images
parameters.
These methods simplify the process of integrating OpenAI functionalities into your applications, allowing for both
standard and streaming interactions.

## Motivation
We are building a client for testing the OpenAI API. This client doesn't actually send requests to the OpenAI API 
but can inspect requests and responses. It's useful for validating whether an agent built using XYZ is functioning 
correctly.
"""


import os
import time
import traceback
from typing import Generator

from dotenv import load_dotenv
from openai import OpenAIError
from openai import OpenAI
from openai import Stream
from openai.types.chat import ChatCompletion, ChatCompletionChunk

__all__ = ["OpenAIClient"]


class TestClient:
    """
    The OpenAI client which uses the OpenAI API to generate responses to messages.
    """
    client: OpenAI
    generate_args: dict
    last_time_price: float

    def __init__(self, api_key=None, **generate_args):
        """Initializes the OpenAI Client.

        Parameters
        ----------
        api_key : str, optional
            The OpenAI API key.
        generate_args : dict, optional
            Arguments for the chat completion request.
            ref: https://platform.openai.com/docs/api-reference/chat/create
        """

        try:
            if api_key is None:
                load_dotenv()
                api_key = os.getenv('OPENAI_API_KEY')
            self.client = OpenAI(api_key=api_key)
        except OpenAIError:
            raise OpenAIError("The OpenAI client is not available. Please check the OpenAI API key.")

        # Set the default generate arguments for OpenAI's chat completions
        self.generate_args = {
            "model": "gpt-4-turbo",
            "temperature": 0.,
            "top_p": 1.0
        }
        # If the user provides generate arguments, update the default values
        self.generate_args.update(generate_args)

    def run(self, messages: list, tools: list = None,
            images: list = None) -> ChatCompletion | Stream[ChatCompletionChunk]:
        """
        Run the assistant with the given messages.

        Parameters
        ----------
        messages : list
            A list of messages to be processed by the assistant.
        tools : list, optional
            A list of tools to be used by the assistant, by default [].
        images : list, optional
            A list of image URLs to be used by the assistant, by default [].

        Returns
        -------
        str
            The assistant's response to the messages.

        Raises
        ------
        OpenAIError
            There may be different errors in different situations, which need to be handled according to the actual
                situation. An error message is printed in the console when an error is reported.
            ref: https://platform.openai.com/docs/guides/error-codes/python-library-error-types
        """
        
        # TODO: 检测 self.generate_args 是不是都是合法的 OpenAI ChatCompletion 参数
        
        # TODO: 根据 OpenAI ChatCompletion 的返回，构造一个虚拟的success_response
        
        # TODO: 检查 messages 是不是合法的
        
        # TODO: 如果有 tools，检查 tools 是不是合法的
        

        if images:
            last_message = messages.pop()
            text = last_message['content']
            content = [
                {"type": "text", "text": text},
            ]
            for image_url in images:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,
                    },
                })
            messages.append({
                "role": last_message['role'],
                "content": content
            })

        # If the user provides tools, use them; otherwise, this client will not use any tools
        if tools:
            tool_choice = "auto"
            local_tools = tools
            # noinspection PyUnusedLocal
            tools = None  # pyright: ignore[reportIncompatibleVariableOverride]
        else:
            local_tools = []
            tool_choice = "none"

        
        
        return success_response

    def stream_run(self, messages: list, images: list) -> Generator[str, None, None]:
        """
        Run the assistant with the given messages in a streaming manner.

        Parameters
        ----------
        images : list
            A list of image URLs to be used by the assistant.
        messages : list
            A list of messages to be processed by the assistant.

        Yields
        ------
        str
            The assistant's response to the messages, yielded one piece at a time.

        Raises
        ------
        OpenAIError
            There may be different errors in different situations, which need to be handled according to the actual
                situation. An error message is printed in the console when an error is reported.
            ref: https://platform.openai.com/docs/guides/error-codes/python-library-error-types
        """
        
        # TODO: 结合 self.run，做同样的检测。并根据 stream 作出适配。

        if images:
            last_message = messages.pop()
            text = last_message['content']
            content = [
                {"type": "text", "text": text},
            ]
            for image_url in images:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,
                    },
                })
            messages.append({
                "role": last_message['role'],
                "content": content
            })

        get_response_signal = False
        count = 0
        while not get_response_signal and count < 10:
            try:
                for response in self.client.chat.completions.create(
                        messages=messages,
                        stream=True,
                        timeout=5,
                        **self.generate_args
                ):
                    if response.choices[0].delta.content is None:
                        return None
                    else:
                        text = response.choices[0].delta.content
                        yield text
            except OpenAIError:
                error_message = str(traceback.format_exc())
                count += 1
                if count == 10:
                    raise OpenAIError(f"The error: {error_message}")
                print(f"The error: {error_message}")
                print(f"The messages: {messages}")
                time.sleep(2)
