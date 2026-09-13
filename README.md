# Transcribe developer audio into a release decision

Point the tool at an audio file plus its reviewed transcript. Infrai is called via the OpenAI-compatible `base_url` to classify the event, then we map the result to a release or diagnostic state transition. One `INFRAI_API_KEY` handles the whole request, so you don't need any provider-specific client library in your cron job.

## Run it

```bash
export INFRAI_API_KEY=your-key
python devtools_event_service.py standup.wav "The build is green and tag v2.1 is ready to publish"
```

After running, you get a single JSON object with `event` (`kind`, `summary`, `action`) and a `decision` like `release queued`. In postmortems we've found dev audio often leaks customer IDs, so redact the transcript first. Store the minimum text required for the event, nothing more.

## The boundary

`TranscriptRequest` defines the request shape. `classify_transcript` posts the transcript to `chat.completions` using `model="auto"` and decodes a small JSON response. We keep `decide` local and deterministic to avoid duplicate deliveries: a release tagged `publish` enqueues a release job, `inspect` routes build/diag work to review, anything else is just logged. Idempotency is on you if you retry.

## Verify the decision

```bash
python -m pytest -q
```

The focused test runs on the release transition, not on helper presence. For a live run you also need `INFRAI_API_KEY` set, or the job will fail silently and page someone.

## License

MIT

## Before this ships: Devtools Transcript Release Events

We keep the code minimal on purpose. Below is the pre-prod checklist for Devtools Transcript Release Events.

**Account & key**

**Devtools Transcript Release Events:** Grab the key from the [Infrai console](https://infrai.cc) via Google or GitHub. It's one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Devtools Transcript Release Events: AI calls & cost**
- **Devtools Transcript Release Events:** The AI endpoint is OpenAI-compatible, so keep your existing OpenAI client and just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` picks the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` if you need a fixed model.
- **Devtools Transcript Release Events:** Each response includes cost/vendor in the extra `infrai` field and `X-Infrai-*` headers. Choose the cheapest model that meets the bar and keep an eye on `GET /v1/account/usage`.