"""The latency numbers. This file is the point of the project.

Every entry carries a ``source`` and ``date`` so a number is never a bare guess.
The seed values here are Mahimai estimates as of the date shown: aggregated from
public and community sources, not measured on your system and not vendor-published
unless a ``source`` says so. They are approximate and will drift as providers
change. If you have a stronger source (measured, ideally with a screenshot), open
a PR and cite it (see CONTRIBUTING.md).

All values are milliseconds, as (p50, p95) pairs.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Entry:
    """One measurable component: its typical (p50) and tail (p95) latency."""

    p50: float
    p95: float
    source: str = "Mahimai estimate"
    date: str = "2026-08"
    notes: str = ""

    def pair(self) -> tuple[float, float]:
        return (self.p50, self.p95)


@dataclass(frozen=True)
class Transport:
    net_in: tuple[float, float]
    jitter: tuple[float, float]
    net_out: tuple[float, float]
    source: str = "Mahimai estimate"
    date: str = "2026-08"
    notes: str = ""


# ── Transport: raw network + jitter buffer, per access type ──────────────────
TRANSPORT: dict[str, Transport] = {
    "PSTN / SIP": Transport((55, 95), (55, 110), (55, 95), notes="carrier trunk + jitter buffer"),
    "WebRTC": Transport((22, 45), (28, 60), (22, 45)),
    "Web only": Transport((12, 28), (18, 40), (12, 28), notes="same-continent WebRTC, no PSTN leg"),
}

# ── Cascaded pipeline: speech to text ────────────────────────────────────────
STT: dict[str, Entry] = {
    "Deepgram Nova-3": Entry(90, 150),
    "AssemblyAI Universal": Entry(130, 210),
    "OpenAI gpt-4o-transcribe": Entry(180, 300),
    "Azure Speech": Entry(160, 260),
    "Google STT v2": Entry(170, 280),
    "Self-hosted (Whisper)": Entry(220, 420, notes="whisper.cpp / faster-whisper, one GPU"),
}

# ── Cascaded pipeline: language model (time to first token) ───────────────────
LLM: dict[str, Entry] = {
    "GPT-4o mini": Entry(280, 480),
    "GPT-4o": Entry(380, 620),
    "Claude Haiku": Entry(260, 430),
    "Claude Sonnet": Entry(420, 700),
    "Gemini Flash": Entry(240, 400),
    "Self-hosted (Llama)": Entry(320, 900, notes="vLLM, depends heavily on batch + hardware"),
}

# ── Cascaded pipeline: text to speech (time to first byte) ────────────────────
TTS: dict[str, Entry] = {
    "Cartesia Sonic": Entry(90, 150),
    "ElevenLabs Flash": Entry(120, 200),
    "ElevenLabs Turbo": Entry(180, 300),
    "Deepgram Aura": Entry(110, 180),
    "Azure Neural": Entry(200, 330),
    "Self-hosted (XTTS)": Entry(260, 520),
}

# ── Realtime speech-to-speech models (time to first audio) ───────────────────
# One model replaces STT + LLM + TTS. Numbers are the model's own response
# time, excluding transport and endpointing (those are separate hops).
REALTIME: dict[str, Entry] = {
    "OpenAI GPT Realtime": Entry(340, 700, source="Mahimai estimate", notes="gpt-4o-realtime"),
    "OpenAI GPT Realtime mini": Entry(280, 560, source="Mahimai estimate", notes="gpt-4o-mini-realtime"),
    "Gemini Live (Flash)": Entry(320, 660, source="Mahimai estimate", notes="gemini-2.0-flash-live"),
    "Gemini Live (native audio)": Entry(360, 720, source="Mahimai estimate"),
    "Amazon Nova Sonic": Entry(300, 620, source="Mahimai estimate"),
    "Self-hosted (Moshi)": Entry(220, 500, source="Mahimai estimate", notes="full-duplex, low latency"),
}

# ── Orchestration frameworks: added overhead (VAD, buffering, turn mgmt) ──────
FRAMEWORKS: dict[str, Entry] = {
    "None (raw)": Entry(0, 0, source="baseline"),
    "LiveKit Agents": Entry(15, 45, source="Mahimai estimate"),
    "Pipecat": Entry(20, 55, source="Mahimai estimate"),
    "Google ADK (bidi streaming)": Entry(25, 70, source="Mahimai estimate"),
    "VoiceGateway": Entry(12, 35, source="Mahimai estimate", notes="mahimai open-source gateway"),
}

# ── Model constants: the methodology, not provider data ──────────────────────
# These change rarely and describe how the hops combine, not who is fast.
MODEL: dict = {
    "cross_region": (45, 90),
    "cross_region_tts_share": 0.4,
    "semantic": {"factor": 0.55, "model": (110, 190)},
    "silence_p95_factor": 1.15,
    "load": {"p50": 0.10, "p95": 0.45},
    "thresholds": {"good": 800, "warn": 1200},
}

# Hop colours for the budget bar (mahimai violet ramp), shared with the website.
COLORS: list[str] = ["#d8c2ff", "#bfa0fa", "#a77cff", "#8f57f7", "#794bcf", "#65408a", "#4a2f6b", "#3a2553"]
