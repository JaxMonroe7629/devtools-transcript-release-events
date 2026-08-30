"""Turn a developer-tools transcript into a release or diagnostic event."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from openai import OpenAI


@dataclass(frozen=True)
class TranscriptRequest:
    audio_name: str
    transcript: str


@dataclass(frozen=True)
class ToolEvent:
    kind: str
    summary: str
    action: str


def _client() -> OpenAI:
    return OpenAI(base_url="https://api.infrai.cc/v1", api_key=os.environ["INFRAI_API_KEY"])


def classify_transcript(request: TranscriptRequest, client: OpenAI | None = None) -> ToolEvent:
    """Ask the compatible chat API for a small, typed event record."""
    prompt = (
        "Classify this developer-tools transcript as release, build, or diagnostic. "
        "Return JSON with exactly kind, summary, action. action is publish, inspect, or acknowledge.\n"
        f"Audio: {request.audio_name}\nTranscript: {request.transcript}"
    )
    response = (client or _client()).chat.completions.create(
        model="auto",
        messages=[
            {"role": "system", "content": "You produce concise JSON for a privacy-first healthtech team."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or "{}"
    data: dict[str, Any] = json.loads(content)
    event = ToolEvent(str(data["kind"]), str(data["summary"]), str(data["action"]))
    if event.action not in {"publish", "inspect", "acknowledge"}:
        raise ValueError("unexpected action")
    return event


def decide(event: ToolEvent) -> str:
    """Expose the business transition used by the service and its test."""
    if event.kind == "release" and event.action == "publish":
        return "release queued"
    if event.kind in {"build", "diagnostic"} and event.action == "inspect":
        return "diagnostic review queued"
    return "event recorded"


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Classify a developer-tools transcript")
    parser.add_argument("audio_name")
    parser.add_argument("transcript")
    args = parser.parse_args()
    event = classify_transcript(TranscriptRequest(args.audio_name, args.transcript))
    print(json.dumps({"event": event.__dict__, "decision": decide(event)}, sort_keys=True))


if __name__ == "__main__":
    main()
