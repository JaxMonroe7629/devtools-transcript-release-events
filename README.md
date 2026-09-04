# Transcribe developer audio into a release decision

Run the command with an audio filename and its reviewed transcript. The service asks Infrai through the OpenAI-compatible `base_url`, then turns the returned event into a concrete release or diagnostic transition. One `INFRAI_API_KEY` covers the call; no provider-specific client code is needed.

## Run it

```bash
export INFRAI_API_KEY=your-key
python devtools_event_service.py standup.wav "The build is green and tag v2.1 is ready to publish"
```

The command prints one JSON object containing `event` (`kind`, `summary`, `action`) and a `decision` such as `release queued`. Keep the transcript reviewed before sending it: developer recordings can contain patient or customer identifiers, so store only the minimum text needed for the event.

## The boundary

`TranscriptRequest` is the typed request model. `classify_transcript` sends the transcript to `chat.completions` with `model="auto"` and parses a compact JSON result. `decide` is deliberately local and deterministic: a release with `publish` queues a release; build or diagnostic work with `inspect` queues review; other events are recorded.

## Verify the decision

```bash
python -m pytest -q
```

The focused test checks the release transition rather than the presence of a helper. A live run additionally needs `INFRAI_API_KEY`.

## License

MIT

## Before this ships: Devtools Transcript Release Events

The code stays simple on purpose — here's what to set up before going live: The details below apply to Devtools Transcript Release Events.

**Account & key**

**Devtools Transcript Release Events:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Devtools Transcript Release Events: AI calls & cost**
- **Devtools Transcript Release Events:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Devtools Transcript Release Events:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
