"""The latency model.

A turn's latency is the sum of independent hops. The p50 total is the sum of
per-hop p50s. Percentiles do not add, so the p95 total adds the per-hop spreads
(p95 - p50) in quadrature on top of the p50 total. Two architectures:

- cascaded: network in, jitter, STT, endpointing, LLM, TTS, network out
- realtime: network in, jitter, endpointing, one speech-to-speech model, network out

An orchestration framework, if any, adds one overhead hop. This mirrors the
website calculator exactly (default cascaded turn = 1326 ms p50 / 1589 ms p95).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from . import data


def _r(x: float) -> int:
    """Round half up, matching JavaScript Math.round for positive values."""
    return int(math.floor(x + 0.5))


@dataclass
class Hop:
    key: str
    label: str
    p50: int
    p95: int
    color: str = ""

    def share(self, total: int) -> float:
        return (self.p50 / total * 100) if total else 0.0


@dataclass
class Estimate:
    rows: list[Hop]
    total_p50: int
    total_p95: int
    max_hop: str
    verdict: str

    def to_dict(self) -> dict:
        return {
            "rows": [
                {"key": h.key, "label": h.label, "p50": h.p50, "p95": h.p95,
                 "color": h.color, "share": round(h.share(self.total_p50), 1)}
                for h in self.rows
            ],
            "total_p50": self.total_p50,
            "total_p95": self.total_p95,
            "max_hop": self.max_hop,
            "verdict": self.verdict,
        }


def verdict(total_p95: int) -> str:
    th = data.MODEL["thresholds"]
    if total_p95 <= th["good"]:
        return "Comfortably under 800ms. Callers will pause and wait for the agent."
    if total_p95 <= th["warn"]:
        return "Above the 800ms threshold where callers start talking over the agent."
    return (
        "Past 1,200ms. Callers assume the line dropped and start repeating themselves, "
        "which costs another turn."
    )


def estimate(
    *,
    mode: str = "cascaded",  # "cascaded" | "realtime"
    transport: str = "PSTN / SIP",
    stt: str = "Deepgram Nova-3",
    llm: str = "GPT-4o mini",
    tts: str = "Cartesia Sonic",
    realtime: str = "OpenAI GPT Realtime",
    framework: str = "None (raw)",
    same_region: bool = True,
    turn: str = "silence",  # "silence" | "semantic"
    endpointing: int = 700,
    calls: int = 25,
) -> Estimate:
    """Estimate the per-turn latency budget. Keyword-only for readability."""
    t = data.TRANSPORT[transport]
    reg = (0.0, 0.0) if same_region else data.MODEL["cross_region"]
    l50 = 1 + (calls / 500) * data.MODEL["load"]["p50"]
    l95 = 1 + (calls / 500) * data.MODEL["load"]["p95"]

    if turn == "semantic":
        sem = data.MODEL["semantic"]
        e50 = endpointing * sem["factor"] + sem["model"][0]
        e95 = endpointing * sem["factor"] + sem["model"][1]
    else:
        e50 = float(endpointing)
        e95 = endpointing * data.MODEL["silence_p95_factor"]

    raw: list[tuple[str, str, float, float]] = [
        ("netIn", "Network in", t.net_in[0], t.net_in[1]),
        ("jitter", "Jitter buffer", t.jitter[0], t.jitter[1]),
    ]

    if mode == "realtime":
        m = data.REALTIME[realtime]
        raw.append(("endp", "Endpointing wait", e50, e95))
        raw.append(("model", "Realtime model response", (m.p50 + reg[0]) * l50, (m.p95 + reg[1]) * l95))
    else:
        st, lm, ts = data.STT[stt], data.LLM[llm], data.TTS[tts]
        share = data.MODEL["cross_region_tts_share"]
        raw.append(("stt", "STT finalisation", st.p50 * l50, st.p95 * l95))
        raw.append(("endp", "Endpointing wait", e50, e95))
        raw.append(("llm", "LLM time to first token", (lm.p50 + reg[0]) * l50, (lm.p95 + reg[1]) * l95))
        raw.append(("tts", "TTS time to first byte",
                    (ts.p50 + reg[0] * share) * l50, (ts.p95 + reg[1] * share) * l95))

    raw.append(("netOut", "Network out", t.net_out[0], t.net_out[1]))

    fw = data.FRAMEWORKS[framework]
    if fw.p50 or fw.p95:
        raw.append(("framework", f"Framework ({framework})", fw.p50, fw.p95))

    rows = [
        Hop(k, label, _r(p50), _r(p95), color=data.COLORS[i % len(data.COLORS)])
        for i, (k, label, p50, p95) in enumerate(raw)
    ]
    total_p50 = sum(h.p50 for h in rows)
    spread = math.sqrt(sum((h.p95 - h.p50) ** 2 for h in rows))
    total_p95 = _r(total_p50 + spread)
    max_hop = max(rows, key=lambda h: h.p50).key
    return Estimate(rows, total_p50, total_p95, max_hop, verdict(total_p95))
