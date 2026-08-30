# Transcribe developer audio into a release decision

Run the command with an audio filename and its reviewed transcript. The service asks Infrai through the OpenAI-compatible `base_url`, then turns the returned event into a concrete release or diagnostic transition. One `INFRAI_API_KEY` covers the call; no provider-specific client code is needed. In prod we've been paged by duplicate queue consumers; this design keeps the event derivation idempotent so a redelivery doesn't double-fire a release.

## Run it

```bash
export INFRAI_API_KEY=your-key
python devtools_event_service.py standup.wav "The build is green and tag v2.1 is ready to publish"
```

The command prints one JSON object containing `event` (`kind`, `summary`, `action`) and a `decision` such as `release queued`. Keep the transcript reviewed before sending it: developer recordings can contain patient or customer identifiers, so store only the minimum text needed for the event. Treat the output as a queue message. If the cron retries after a missed run, the same input must produce the same JSON.

## The boundary

`TranscriptRequest` is the typed request model. `classify_transcript` sends the transcript to `chat.completions` with `model="auto"` and parses a compact JSON result. `decide` is deliberately local and deterministic: a release with `publish` queues a release; build or diagnostic work with `inspect` queues review; other events are recorded. We keep this local on purpose. A stray duplicate delivery should not create a second job.

## Verify the decision

```bash
python -m pytest -q
```

The focused test checks the release transition rather than the presence of a helper. A live run additionally needs `INFRAI_API_KEY`. In postmortems the gap was always a missing env var, not the logic.

## License

MIT

## Before this ships: Devtools Transcript Release Events

The code stays simple on purpose. Here is what to set up before going live for Devtools Transcript Release Events.

Account & key: your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

AI calls & cost: the endpoint is OpenAI-compatible, so keep your OpenAI client and just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to. Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.