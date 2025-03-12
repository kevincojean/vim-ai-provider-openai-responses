import vim
import json
from collections.abc import Sequence, Mapping, Iterator
from typing import TypedDict, Literal, Union, List, Protocol, Tuple, Any
import urllib.request
import os

class AITextContent(TypedDict):
    type: Literal['text']
    text: str

class AIImageUrlContent(TypedDict):
    type: Literal['image_url']
    image_url: dict[str, str]  # {'url': str}

AIMessageContent = Union[AITextContent, AIImageUrlContent]

class AIMessage(TypedDict):
    role: Literal['system', 'user', 'assistant']
    content: List[AIMessageContent]

class AIUtils(Protocol):
    def print_debug(self, text: str, *args: Any):
        pass
    def make_known_error(self, message: str):
        pass
    def load_api_key(self, env_variable: str, file_path: str):
        pass

class AIResponseChunk(TypedDict):
    type: Literal['assistant', 'thinking']
    content: str

AICommandType = Literal['chat', 'edit', 'complete'] # image not yet supported

class AIProvider(Protocol):
    def __init__(self, command_type: AICommandType, raw_options: Mapping[str, str], utils: AIUtils) -> None:
        pass

    def request(self, messages: Sequence[AIMessage]) -> Iterator[AIResponseChunk]:
        pass

class GoogleAIProvider():

    def __init__(self, command_type: AICommandType, raw_options: Mapping[str, str], utils: AIUtils) -> None:
        self.utils = utils
        self.command_type = command_type
        raw_default_options = vim.eval(f"g:vim_ai_google_config")

        self.options = {**raw_default_options, **raw_options}
        for key, value in self.options.items():
            if isinstance(value, str) and value.replace('.', '', 1).isdigit():
                self.options[key] = float(value)

    def _protocol_type_check(self) -> None:
        # dummy method, just to ensure type safety
        utils: AIUtils
        options: Mapping[str, str] = {}
        provider: AIProvider = GoogleAIProvider('chat', options, utils)

    def request(self, messages: Sequence[AIMessage]) -> Iterator[AIResponseChunk]:
        RESP_DATA_PREFIX = 'data: '
        RESP_DONE = '[DONE]'

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "VimAI",
        }
        api_key = self.utils.load_api_key("GEMINI_API_KEY", self.options.get('token_file_path', ''))

        generationConfig = {
            "temperature": self.options.get('temperature') or None,
            "maxOutputTokens": self.options.get('max_output_tokens') or None,
            "topP": self.options.get('top_p') or None,
            "topK": self.options.get('top_k') or None
        }

        system_instruction = None
        contents = []
        for message in messages:
            if message['role'] == 'system' and message['content'][0]['type'] == 'text':
                system_instruction = {'parts': {'text': message['content'][0]['text']}}
                continue
            role = 'model' if message['role'] == 'assistant' else 'user'
            parts = []
            for content in message['content']:
                if content['type'] != 'text':
                    raise self.utils.make_known_error(f'google provider: content type {content["type"]} not implemented')
                parts.append({'text': content['text']})
            contents.append({'role': role, 'parts': parts})

        url = f"{self.options['endpoint_url']}/{self.options['model']}:streamGenerateContent?alt=sse&key={api_key}"
        data = {
            "system_instruction": system_instruction,
            "contents": contents,
            "generationConfig": generationConfig,
        }
        self.utils.print_debug("openai: [{}] request: {}", self.command_type, data)

        request_timeout=self.options['request_timeout']
        req = urllib.request.Request(
            url,
            data=json.dumps({ **data }).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=request_timeout) as response:
            for line_bytes in response:
                line = line_bytes.decode("utf-8", errors="replace")
                if not line.startswith(RESP_DATA_PREFIX):
                    continue
                line_data = line[len(RESP_DATA_PREFIX):-1]
                if line_data.strip() == RESP_DONE:
                    pass
                else:
                    resp_chunk = json.loads(line_data)
                    self.utils.print_debug("openai: [{}] response: {}", self.command_type, resp_chunk)
                    candidate = resp_chunk['candidates'][0]
                    text = candidate['content']['parts'][0]['text']
                    text = text.rstrip() if 'finishReason' in candidate else text # strip as models often leaves blank line at the end
                    yield {'type': 'assistant', 'content': text}
