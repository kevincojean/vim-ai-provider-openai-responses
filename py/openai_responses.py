from collections.abc import Sequence, Mapping, Iterator
from typing import TypedDict, Literal, Union, List, Protocol, Any

import openai
from openai import Stream
from openai.types.responses import ResponseInputParam, Response, ResponseStreamEvent


class AITextContent(TypedDict):
    type: Literal['text']
    text: str


class AIImageUrlContent(TypedDict):
    type: Literal['image_url']
    image_url: dict[str, str]  # {'url': str}


AIMessageContent = Union[AITextContent, AIImageUrlContent]


class AIMessage(TypedDict):
    role: Literal['system', 'user', 'assistant', 'developer']
    content: List[AIMessageContent]


class AIUtils(Protocol):
    def print_debug(self, text: str, *args: Any):
        pass

    def make_known_error(self, message: str):
        pass

    def load_api_key(self, env_variable: str, token_file_path: str = "", token_load_fn: str = ""):
        pass


class AIResponseChunk(TypedDict):
    type: Literal['assistant', 'thinking']
    content: str


class AIImageResponseChunk(TypedDict):
    b64_data: str


AICommandType = Literal['chat', 'edit', 'complete', 'image']


class AIProvider(Protocol):
    def __init__(self, command_type: AICommandType, raw_options: Mapping[str, str], utils: AIUtils) -> None:
        pass

    def request(self, messages: Sequence[AIMessage]) -> Iterator[AIResponseChunk]:
        pass

    def request_image(self, prompt: str) -> list[AIImageResponseChunk]:
        pass


class OpenAiResponsesProvider:
    """
    OpenAiResponsesProvider backed by the OpenAI python package.
    """

    def __init__(self, command_type: AICommandType,
                 raw_options: Mapping[str, str],
                 utils: AIUtils,
                 under_test: bool = False) -> None:
        self.utils = utils
        self.command_type = command_type
        raw_default_options = {}
        if not under_test:
            import vim
            raw_default_options = vim.eval(f"g:vim_ai_openai_responses_config")
        self.options = {**raw_default_options, **raw_options}
        self.options = {**raw_options}
        for key, value in self.options.items():
            if isinstance(value, str) and value.replace('.', '', 1).isdigit():
                self.options[key] = float(value)

        if 'stream' in self.options:
            self.options['stream'] = self._coerce_to_bool(self.options['stream'])

    def _coerce_to_bool(self, value: str) -> bool:
        if isinstance(value, str):
            return value.strip().lower() in ['true', '1', 't', 'y', 'yes']
        return bool(value)

    def _protocol_type_check(self) -> None:
        # dummy method, just to ensure type safety
        utils: AIUtils
        options: Mapping[str, str] = {}
        provider: AIProvider = OpenAiResponsesProvider('chat', options, utils)

    def request(self, messages: Sequence[AIMessage]) -> Iterator[AIResponseChunk]:
        """
        Example: https://github.com/openai/openai-python/blob/main/examples/streaming.py
        """
        openai_response = openai.responses.create(input=[self._map_to_response_input_param(m) for m in messages],
                                           model=self.options['model'],
                                           stream=self.options['stream'])
        if not self.options['stream']:
            openai_response: Response
            response_type = openai_response.output[0].role
            response_text = openai_response.output[0].content[0].text
            response_chunk_type = response_type if response_type == "assistant" else "thinking"
            yield {
                "type": response_chunk_type,
                "content": response_text,
            }
        if self.options['stream']:
            openai_response: Stream[ResponseStreamEvent]
            for response_event in openai_response:
                if response_event.type == 'response.content_part.added':
                    yield {
                        "type": "assistant",
                        "content": response_event.part.text,
                    }
                elif response_event.type == 'response.output_text.delta':
                    yield {
                        "type": "assistant",
                        "content": response_event.delta,
                    }
                elif response_event.type == 'response.completed':
                    return
                elif response_event.type == 'error':
                    raise Exception(f"Error (code: {response_event.code}) - {response_event.message}")
                else:
                    continue
                    # Expected events, which may or may not need to be handled.
                    # {
                    #     'response.content_part.done',
                    #     'response.created',
                    #     'response.failed',
                    #     'response.file_search_call.completed',
                    #     'response.file_search_call.in_progress',
                    #     'response.file_search_call.searching',
                    #     'response.function_call_arguments.delta',
                    #     'response.function_call_arguments.done',
                    #     'response.in_progress',
                    #     'response.incomplete',
                    #     'response.output_item.added',
                    #     'response.output_item.done',
                    #     'response.output_text.annotation.added',
                    #     'response.output_text.done',
                    #     'response.reasoning_summary_part.added',
                    #     'response.reasoning_summary_part.done',
                    #     'response.reasoning_summary_text.delta',
                    #     'response.reasoning_summary_text.done',
                    #     'response.refusal.delta',
                    #     'response.refusal.done',
                    #     'response.web_search_call.completed',
                    #     'response.web_search_call.in_progress',
                    #     'response.web_search_call.searching',
                    # }

    def _map_to_response_input_param(self, message: AIMessage) -> ResponseInputParam:
        if not message['content']:
            return {
                'content': "",
                'role': message['role'],
                'type': 'message',
            }

        first_content_element = message['content'][0]
        if isinstance(first_content_element, str):
            return {
                'content': first_content_element,
                'role': message['role'],
                'type': 'message',
            }
        elif isinstance(first_content_element, dict):
            content = first_content_element['image_url'] \
                if 'image_url' in first_content_element.keys() \
                else first_content_element['text']
            return {
                'content': content,
                'role': message['role'],
                'type': 'message',
            }
        else:
            raise Exception(f"Handling of `{first_content_element.__class__.__name__}` messages not implemented.")

