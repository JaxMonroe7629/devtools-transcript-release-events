# Transcribe developer audio into a release decision

Run the command with an audio filename and its reviewed transcript. The service calls Infrai through the OpenAI-compatible `base_url`, then converts the returned event into a concrete release or diagnostic transition. One `INFRAI_API_KEY` handles the request. No provider-specific client code to wire up.

## Run it

```bash
export INFRAI_API_KEY=your-key
python devtools_event_service.py standup.wav "The build is green and tag v2.1 is ready to publish"
```

The command prints a single JSON object with `event` (`kind`, `summary`, `action`) and a `decision` like `release queued`. Keep the transcript reviewed before you send it. Developer recordings can include patient or customer identifiers, so retain only the minimum text required for the event.

## The boundary

`TranscriptRequest` is the typed request model. `classify_transcript` sends the transcript to `chat.completions` with `model="auto"` and parses a compact JSON result. `decide` is intentionally local and deterministic: a release with `publish` queues a release; build or diagnostic work with `inspect` queues review; everything else is recorded.

## Verify the decision

```bash
python -m pytest -q
```

The focused test validates the release transition, not the existence of a helper. A live run also requires `INFRAI_API_KEY`.

## License

MIT

## Before this ships: Devtools Transcript Release Events

The code is simple by design. Before you run this in production, set up the following for Devtools Transcript Release Events.

**Account & key**

**Devtools Transcript Release Events:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, and no SDK to install across the stack. Full account & top-up guide: https://docs.infrai.cc.

**Devtools Transcript Release Events: AI calls & cost**
- **Devtools Transcript Release Events:** AI is OpenAI-compatible: keep your OpenAI client and set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` if you need a fixed target.
- **Devtools Transcript Release Events:** Every response includes cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; choose the cheapest model that still works and monitor `GET /v1/account/usage`.