"""Unit tests for local Ollama response handling."""

from app.services.copilot import _ollama_answer


def test_ollama_answer_reads_normal_chat_response() -> None:
    body = b'{"message":{"role":"assistant","content":"HackTool means a dual-use utility."}}'

    assert _ollama_answer(body) == "HackTool means a dual-use utility."


def test_ollama_answer_joins_streamed_chat_chunks() -> None:
    body = (
        b'{"message":{"content":"HackTool "},"done":false}\n'
        b'{"message":{"content":"is a detection label."},"done":true}\n'
    )

    assert _ollama_answer(body) == "HackTool is a detection label."


def test_ollama_answer_reads_generate_response() -> None:
    assert _ollama_answer(b'{"response":"A short explanation."}') == "A short explanation."
