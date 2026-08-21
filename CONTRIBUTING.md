# Contributing

The reason this project exists is to keep an honest, current set of voice-agent
latency numbers. The best contribution is a **number with a source**.

## Add or update a provider

1. Open [`src/voice_latency/data.py`](src/voice_latency/data.py).
2. Find the right table: `STT`, `LLM`, `TTS`, `REALTIME` (speech-to-speech),
   `TRANSPORT`, or `FRAMEWORKS`.
3. Add or edit an `Entry(p50, p95, source=..., date="YYYY-MM", notes=...)`.
   - `p50` / `p95` are milliseconds for that component only. For STT/LLM/TTS and
     realtime models this is the component's own response time, not the whole
     turn (transport and endpointing are separate hops).
   - `source` is required. "measured, N=200 calls, us-east" beats "vendor page"
     beats "community estimate". Say what you actually know.
   - `date` is when the number was true (`YYYY-MM`), since providers change.
4. Run the tests: `pip install -e ".[dev]" && pytest`.
5. Open a PR using the template. Explain how you got the number.

## What makes a good PR

- A `source` a reader can weigh. If you measured it, say how, and attach a screenshot of the measurement where you can.
- One provider (or one coherent set) per PR, so it is easy to review.
- Tests pass. If you added a new provider, the export test still holds.

## What this is not

Not a marketing leaderboard. We do not rank vendors, and "self-hosted" is a first
class option. If a number makes a provider look good or bad, the source is what
decides whether it stays.

## New categories or a new model type

Adding a whole new realtime model, transport type, or framework is welcome. Keep
the shape (`Entry` with a source), and add it to the matching table. If the
*math* needs to change (a genuinely new architecture), open an issue first so we
agree on the model before the code.
