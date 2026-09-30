"""Harness tests that do not call the OpenAI API.

Run from the repo root:

    python -m unittest labs.common.test_harness
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from labs.common.client import DEFAULT_MODEL, settings_from_env
from labs.common.loop import run_file_agent
from labs.common.tools import read_file


DOCS = Path(__file__).resolve().parents[1] / "ch02-your-first-loop" / "docs"


def _tool_response(name: str, arguments: object, call_id: str = "call_1"):
    function = SimpleNamespace(name=name, arguments=arguments)
    call = SimpleNamespace(id=call_id, type="function", function=function)
    message = SimpleNamespace(content=None, tool_calls=[call])
    choice = SimpleNamespace(message=message, finish_reason="tool_calls")
    return SimpleNamespace(choices=[choice])


def _text_response(text: str, finish: str = "stop"):
    message = SimpleNamespace(content=text, tool_calls=None)
    choice = SimpleNamespace(message=message, finish_reason=finish)
    return SimpleNamespace(choices=[choice])


class ScriptedClient:
    def __init__(self, responses: list):
        self.responses = list(responses)
        self.calls: list[dict] = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        # Copy messages now. The loop keeps appending to the same list.
        recorded = dict(kwargs)
        recorded["messages"] = [dict(message) for message in kwargs["messages"]]
        self.calls.append(recorded)
        if not self.responses:
            raise AssertionError("scripted client ran out of responses")
        return self.responses.pop(0)


class SettingsTests(unittest.TestCase):
    def test_default_model_when_unset(self):
        api_key, model = settings_from_env({})
        self.assertEqual(api_key, "")
        self.assertEqual(model, DEFAULT_MODEL)
        self.assertEqual(DEFAULT_MODEL, "gpt-4.1-mini")

    def test_empty_api_key_is_preserved(self):
        api_key, _model = settings_from_env({"OPENAI_API_KEY": "  "})
        self.assertEqual(api_key, "")

    def test_blank_model_uses_default(self):
        _api_key, model = settings_from_env({"MODEL": "  "})
        self.assertEqual(model, DEFAULT_MODEL)

    def test_explicit_values_win(self):
        api_key, model = settings_from_env(
            {
                "OPENAI_API_KEY": "sk-test",
                "MODEL": "gpt-4.1",
            }
        )
        self.assertEqual(api_key, "sk-test")
        self.assertEqual(model, "gpt-4.1")

    def test_legacy_provider_variables_are_ignored(self):
        api_key, model = settings_from_env(
            {
                "BASE_URL": "http://localhost:11434/v1",
                "API_KEY": "ollama",
            }
        )
        self.assertEqual(api_key, "")
        self.assertEqual(model, DEFAULT_MODEL)

    def test_loader_does_not_require_a_committed_secret(self):
        root = Path(__file__).resolve().parents[2]
        self.assertFalse((root / ".env").exists())
        example = (root / ".env.example").read_text(encoding="utf-8")
        self.assertIn("OPENAI_API_KEY=", example)
        self.assertNotIn("sk-proj-", example)
        self.assertNotIn("sk-or-", example)


class ReadFileTests(unittest.TestCase):
    def test_reads_policy_with_path_header(self):
        text = read_file(DOCS, "policy.md")
        self.assertTrue(text.startswith("PATH: docs/policy.md"))
        self.assertIn("14 days", text)
        self.assertIn("final sale", text)

    def test_accepts_docs_prefix_and_dot_slash(self):
        via_prefix = read_file(DOCS, "docs/faq.md")
        via_dot = read_file(DOCS, "./faq.md")
        self.assertTrue(via_prefix.startswith("PATH: docs/faq.md"))
        self.assertTrue(via_dot.startswith("PATH: docs/faq.md"))
        self.assertIn("Closed Monday", via_prefix)

    def test_rejects_escape_and_absolute_paths(self):
        for path in ("../.env", "/etc/passwd", "docs/../../.env", "policy.md/../../.env"):
            result = read_file(DOCS, path)
            self.assertTrue(result.startswith("ERROR"), path)
            self.assertNotIn("API_KEY", result)

    def test_missing_file_lists_markdown(self):
        result = read_file(DOCS, "secret.md")
        self.assertIn("not found", result)
        self.assertIn("policy.md", result)
        self.assertIn("faq.md", result)

    def test_rejects_hidden_names(self):
        result = read_file(DOCS, ".env")
        self.assertTrue(result.startswith("ERROR"))

    def test_symlink_outside_docs_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir()
            (docs / "policy.md").write_text("public", encoding="utf-8")
            secret = root / "secret.md"
            secret.write_text("SECRET-VALUE", encoding="utf-8")
            (docs / "leak.md").symlink_to(secret)
            result = read_file(docs, "leak.md")
            self.assertTrue(result.startswith("ERROR"))
            self.assertNotIn("SECRET-VALUE", result)


class LoopTests(unittest.TestCase):
    def test_tool_call_then_final_answer_with_citation(self):
        client = ScriptedClient(
            [
                _tool_response("read_file", '{"path": "policy.md"}', "call_abc"),
                _text_response(
                    "Opened coffee is final sale (docs/policy.md). "
                    "Pastries are not shipped (docs/policy.md)."
                ),
            ]
        )
        result = run_file_agent(
            client,
            "test-model",
            "Can I return opened beans and ship a bun?",
            DOCS,
            verbose=False,
        )
        self.assertEqual(result.stopped, "final")
        self.assertEqual(result.steps, 2)
        self.assertIn("docs/policy.md", result.text)
        self.assertEqual(len(result.tool_log), 1)
        self.assertEqual(len(client.calls), 2)

        first = client.calls[0]
        self.assertNotIn("tool_choice", first)
        self.assertEqual(first["model"], "test-model")
        self.assertEqual(first["tools"][0]["function"]["name"], "read_file")
        self.assertNotIn("name", first["messages"][0])

        second_messages = client.calls[1]["messages"]
        assistant = second_messages[2]
        self.assertEqual(assistant["role"], "assistant")
        self.assertEqual(assistant["tool_calls"][0]["id"], "call_abc")
        self.assertNotIn("name", assistant)
        tool_message = second_messages[3]
        self.assertEqual(tool_message["role"], "tool")
        self.assertEqual(tool_message["tool_call_id"], "call_abc")
        self.assertNotIn("name", tool_message)
        self.assertTrue(tool_message["content"].startswith("PATH: docs/policy.md"))

    def test_invalid_json_is_returned_as_a_tool_error(self):
        client = ScriptedClient(
            [
                _tool_response("read_file", "{not-json"),
                _text_response("I could not read a file (docs/policy.md)."),
            ]
        )
        result = run_file_agent(
            client, "test-model", "question", DOCS, verbose=False
        )
        self.assertEqual(result.stopped, "final")
        tool_message = client.calls[1]["messages"][3]
        self.assertIn("ERROR:", tool_message["content"])
        self.assertIn("not valid JSON", tool_message["content"])

    def test_unknown_tool(self):
        client = ScriptedClient(
            [
                _tool_response("send_email", '{"path": "policy.md"}'),
                _text_response("I can't do that."),
            ]
        )
        result = run_file_agent(
            client, "test-model", "question", DOCS, verbose=False
        )
        self.assertEqual(result.stopped, "final")
        tool_message = client.calls[1]["messages"][3]
        self.assertIn("unknown tool", tool_message["content"])

    def test_max_steps_does_not_invent_an_answer(self):
        client = ScriptedClient(
            [
                _tool_response("read_file", '{"path": "faq.md"}', "c1"),
                _tool_response("read_file", '{"path": "policy.md"}', "c2"),
            ]
        )
        result = run_file_agent(
            client,
            "test-model",
            "question",
            DOCS,
            max_steps=2,
            verbose=False,
        )
        self.assertEqual(result.stopped, "max_steps")
        self.assertEqual(result.steps, 2)
        self.assertIn("max steps", result.text)
        self.assertEqual(len(client.calls), 2)

    def test_repeated_identical_call_stops(self):
        client = ScriptedClient(
            [
                _tool_response("read_file", '{"path": "policy.md"}', "c1"),
                _tool_response("read_file", {"path": "policy.md"}, "c2"),
                _tool_response("read_file", '{"path": "policy.md"}', "c3"),
                _text_response("should not be used"),
            ]
        )
        result = run_file_agent(
            client, "test-model", "question", DOCS, verbose=False
        )
        self.assertEqual(result.stopped, "repeated_call")
        self.assertEqual(result.steps, 3)
        self.assertEqual(len(client.calls), 3)
        # The second identical read includes a nudge, and still returns the file.
        second_tool = client.calls[2]["messages"][-1]["content"]
        self.assertIn("PATH: docs/policy.md", second_tool)
        self.assertIn("already read", second_tool)

    def test_max_tokens_finish_without_tool_calls(self):
        client = ScriptedClient([_text_response("partial", finish="length")])
        result = run_file_agent(
            client, "test-model", "question", DOCS, verbose=False
        )
        self.assertEqual(result.stopped, "max_tokens")
        self.assertIn("partial", result.text)

    def test_arguments_dict_is_accepted(self):
        client = ScriptedClient(
            [
                _tool_response("read_file", {"path": "faq.md"}),
                _text_response("Closed Monday (docs/faq.md)."),
            ]
        )
        result = run_file_agent(
            client, "test-model", "which day are you closed?", DOCS, verbose=False
        )
        self.assertEqual(result.stopped, "final")
        self.assertIn("Closed Monday", result.text)
        encoded = client.calls[1]["messages"][2]["tool_calls"][0]["function"]["arguments"]
        self.assertIsInstance(encoded, str)
        self.assertEqual(json.loads(encoded)["path"], "faq.md")


if __name__ == "__main__":
    unittest.main()
