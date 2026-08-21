# voice-latency

A per-hop latency budget for voice agents. It models two architectures, cascaded
(STT then LLM then TTS) and realtime (one speech-to-speech model), adds framework
overhead, and tells you where the milliseconds go.

**The numbers are the point.** Every provider figure lives in one Python file
with a `source` and a `date`. If you have measured better, open a PR. That is how
a latency benchmark stays honest.

> **Disclaimer.** These figures are illustrative estimates aggregated from public
> and community sources. They are not measurements of your system, and not
> vendor-published unless a `source` says so. They are approximate, they will
> drift as providers change, and they may simply be wrong. Use them to understand
> where a latency budget goes, not as a basis for SLAs, contracts, or purchasing
> decisions. The software and data are provided "as is", without warranty of any
> kind, and the maintainers accept no liability for any decision made using them.
> Verify against your own stack before you rely on a number.

This package powers the calculator at
[mahimai.ca/tools/latency-calculator](https://mahimai.ca/tools/latency-calculator);
the site reads the same data, so the two never disagree.

## Install

```bash
pip install voice-latency      # or: uv pip install voice-latency
```

## Use it

```python
from voice_latency import estimate

# Cascaded pipeline (default)
e = estimate(stt="Deepgram Nova-3", llm="GPT-4o mini", tts="Cartesia Sonic",
             transport="PSTN / SIP", endpointing=700, calls=25)
print(e.total_p50, e.total_p95)   # 1326 1589
print(e.max_hop)                  # 'endp'  (the endpointing delay you set)

# Realtime, speech-to-speech
r = estimate(mode="realtime", realtime="Gemini Live (Flash)",
             framework="LiveKit Agents", transport="WebRTC")
for hop in r.rows:
    print(f"{hop.label:<26} {hop.p50:>4}ms  p95 {hop.p95}ms")
```

From the terminal:

```bash
voice-latency                                   # default cascaded turn
voice-latency --mode realtime --realtime "OpenAI GPT Realtime"
voice-latency --framework "Google ADK (bidi streaming)" --transport WebRTC
voice-latency list                              # every provider it knows
voice-latency export --out data.json            # the dataset as JSON
```

## The model

A turn's latency is the sum of independent hops. The p50 total sums the per-hop
p50s. Percentiles do not add, so the p95 total adds each hop's spread (p95 minus
p50) in quadrature on top of the p50 total. Hops:

- **cascaded:** network in, jitter, STT, endpointing, LLM, TTS, network out
- **realtime:** network in, jitter, endpointing, speech-to-speech model, network out
- an orchestration **framework**, if any, adds one overhead hop

Constants (cross-region penalty, concurrency load, endpointing math, thresholds)
live in `MODEL` in `src/voice_latency/data.py`.

## The data

All of it is in [`src/voice_latency/data.py`](src/voice_latency/data.py): STT,
LLM, TTS, realtime speech-to-speech models, transport, and frameworks. Figures
are illustrative defaults unless a `source` says otherwise. They are not
vendor-published or independently benchmarked.

**Improve them.** See [CONTRIBUTING.md](CONTRIBUTING.md). A PR that adds a source
is worth more than a PR that just changes a number.

## License

MIT.
