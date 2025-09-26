import random
import tempfile
from pathlib import Path
from typing import Any, Generator
from unittest import TestCase

from py.openai_responses import OpenAiResponsesProvider, AIUtils, LoggingConfiguration


class TestOpenAiResponsesProvider(TestCase):

    TEST_MODEL = "gpt-4.1-nano"

    AI_COMMAND_TYPES = ['chat', 'edit', 'complete', 'image']

    def test_request(self):
        for command_type in self.AI_COMMAND_TYPES:
            provider = self._create_openai_responses_provider(command_type=command_type)
            response = "".join([d['content'] for d in self._open_open_ai_responses_generator(provider)])
            self.assertNotEqual("", response)

    def test_request_streaming(self):
        for command_type in self.AI_COMMAND_TYPES:
            provider = self._create_openai_responses_provider(command_type=command_type, stream=True)
            response = "".join([d['content'] for d in self._open_open_ai_responses_generator(provider)])
            self.assertNotEqual("", response)

    def test_initial_prompt_is_passed_as_an_option(self):
        for command_type in self.AI_COMMAND_TYPES:
            initial_prompt = "You only answer with 'I LOVE MAHJONG'."
            provider = self._create_openai_responses_provider(
                command_type=command_type,
                extra_options={'initial_prompt': initial_prompt})
            response = "".join([d['content'] for d in self._open_open_ai_responses_generator(provider)])
            self.assertIn('I LOVE MAHJONG', response)

    def test_logging(self):
        provider = self._create_openai_responses_provider(
            command_type='chat',
            logging_configuration=self._create_enabled_logging_configuration())
        next(self._open_open_ai_responses_generator(provider))
        self.assertLogs(provider.logger_plugin)
        self._assert_file_is_not_empty(provider.logging_file)
        self.assertNoLogs(provider.logger_open_ai)

    def test_logging_disabled(self):
        provider = self._create_openai_responses_provider(
            command_type='chat',
            logging_configuration=self._create_disabled_logging_configuration())
        next(self._open_open_ai_responses_generator(provider))
        self.assertIsNone(provider.logging_file)
        self.assertNoLogs(provider.logger_plugin)
        self.assertNoLogs(provider.logger_open_ai)

    def test_ai_logging(self):
        provider = self._create_openai_responses_provider(
            command_type='chat',
            logging_ai_configuration=self._create_enabled_logging_configuration())
        next(self._open_open_ai_responses_generator(provider))
        self.assertLogs(provider.logger_open_ai)
        self._assert_file_is_not_empty(provider.logging_file_openai)
        self.assertNoLogs(provider.logger_plugin)

    def test_ai_logging_disabled(self):
        provider = self._create_openai_responses_provider(
            command_type='chat',
            logging_ai_configuration=self._create_disabled_logging_configuration())
        next(self._open_open_ai_responses_generator(provider))
        self.assertIsNone(provider.logging_file_openai)
        self.assertNoLogs(provider.logger_plugin)
        self.assertNoLogs(provider.logger_open_ai)

    def _assert_file_is_not_empty(self, file: Path):
        with file.open('r+') as f:
            file_content = "".join(s.strip() for s in f.readlines())
            self.assertNotEqual(file_content, "")

    def _assert_file_is_empty(self, file: Path):
        with file.open('r+') as f:
            file_content = "".join(s.strip() for s in f.readlines())
            self.assertEquals(file_content, "")

    def _create_openai_responses_provider(
            self, command_type: str,
            stream: bool = False,
            logging_configuration: LoggingConfiguration = LoggingConfiguration(enabled=False, file=None),
            logging_ai_configuration: LoggingConfiguration = LoggingConfiguration(enabled=False, file=None),
            extra_options=None
    ):
        if extra_options is None:
            extra_options = {}
        return OpenAiResponsesProvider(
            command_type=command_type,
            raw_options={
                "provider": "openai_responses",
                "stream": stream,
                "model": TestOpenAiResponsesProvider.TEST_MODEL,
            } | extra_options,
            utils=self.TestAIUtils(),
            under_test=True,
            logging_configuration=logging_configuration,
            logging_ai_configuration=logging_ai_configuration
        )

    def _open_open_ai_responses_generator(self, provider: OpenAiResponsesProvider) -> Generator:
        return provider.request([{
            "role": "user",
            "content": [{
                "type": "text",
                "text": "Hello there!"
            }]
        }])

    def _create_enabled_logging_configuration(self):
        f = Path(tempfile.mkstemp()[1])
        return LoggingConfiguration(enabled=True, file=f)

    def _create_disabled_logging_configuration(self):
        return LoggingConfiguration(enabled=True, file=None)

    class TestAIUtils(AIUtils):
        def print_debug(self, text: str, *args: Any):
            pass

        def make_known_error(self, message: str):
            pass

        def load_api_key(self, env_variable: str, token_file_path: str = "", token_load_fn: str = ""):
            pass
