from typing import Any, Generator
from unittest import TestCase

from py.openai_responses import OpenAiResponsesProvider, AIUtils


class TestOpenAiResponsesProvider(TestCase):

    TEST_MODEL = "gpt-4.1-nano"

    AI_COMMAND_TYPES = ['chat', 'edit', 'complete', 'image']

    def test_request(self):
        for command_type in self.AI_COMMAND_TYPES:
            provider = self._create_openai_responses_provider(command_type=command_type)
            response = "".join([d['content'] for d in self._do_openai_responses_request(provider)])
            self.assertNotEqual("", response)

    def test_request_streaming(self):
        for command_type in self.AI_COMMAND_TYPES:
            provider = self._create_openai_responses_provider(command_type=command_type, stream=True)
            response = "".join([d['content'] for d in self._do_openai_responses_request(provider)])
            self.assertNotEqual("", response)

    def _create_openai_responses_provider(self, command_type: str, stream: bool = False):
        return OpenAiResponsesProvider(
            command_type=command_type,
            raw_options={
                "provider": "openai_responses",
                "stream": stream,
                "model": TestOpenAiResponsesProvider.TEST_MODEL,
            },
            utils=self.TestAIUtils(),
            under_test=True
        )

    def _do_openai_responses_request(self, provider) -> Generator:
        return provider.request([{
            "role": "user",
            "content": [{
                "type": "text",
                "text": "Hello there!"
            }]
        }])

    class TestAIUtils(AIUtils):
        def print_debug(self, text: str, *args: Any):
            pass

        def make_known_error(self, message: str):
            pass

        def load_api_key(self, env_variable: str, token_file_path: str = "", token_load_fn: str = ""):
            pass
