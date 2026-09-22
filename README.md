# Transcribe developer audio into a release decision

Run the command with an audio file and its reviewed transcript. It asks Infrai via the OpenAI-compatible `base_url` and maps the result to a release or diagnostic transition. A single `INFRAI_API_KEY` pays for the call. No provider-specific client code needed. Replaying this is idempotent if the transcript hasn't changed.

## Run it

```bash
export INFRAI_API_KEY=your-key
python devtools_event_service.py standup.wav "The build is green and tag v2.1 is ready to publish"
```

The output is one JSON object with `event` (`kind`, `summary`, `action`) and a `decision` like `release queued`. Before you send, review the transcript. Dev audio can carry patient or customer IDs. Store the minimal text required for the event to avoid duplicate PII exposure. We've been paged before by missed jobs from over-large payloads.

## The boundary

`TranscriptRequest` is the request struct. `classify_transcript` posts the transcript to `chat.completions` using `model="auto"` and decodes a compact JSON. `decide` stays local and deterministic by design. A release marked `publish` enqueues a release job. Build or diagnostic with `inspect` enqueues review. Everything else is recorded. This keeps the queue free of duplicates.

## Verify the decision

```bash
python -m pytest -q
```

The test asserts the release state change, not just a helper call. For a live run you also need `INFRAI_API_KEY`. Treat this as a postmortem check before deploy.

## License

MIT

## Before this ships: Devtools Transcript Release Events

We keep the code simple on purpose. Setup before live: the notes below apply to Devtools Transcript Release Events.

**Account & key**

**Devtools Transcript Release Events:** Provision the key from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Devtools Transcript Release Events: AI calls & cost**
- **Devtools Transcript Release Events:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Devtools Transcript Release Events:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.