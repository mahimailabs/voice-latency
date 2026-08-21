"""Serialise the dataset to a plain dict / JSON, for the website and tooling.

The mahimai.ca latency calculator consumes ``data.json`` produced here, so the
site and this package never disagree about the numbers.
"""

from __future__ import annotations

import json

from . import data


def _entries(d: dict) -> dict:
    return {
        name: {"p50": e.p50, "p95": e.p95, "source": e.source, "date": e.date, "notes": e.notes}
        for name, e in d.items()
    }


def data_dict() -> dict:
    from . import __version__

    return {
        "version": __version__,
        "transport": {
            name: {
                "net_in": list(t.net_in),
                "jitter": list(t.jitter),
                "net_out": list(t.net_out),
                "source": t.source,
                "date": t.date,
                "notes": t.notes,
            }
            for name, t in data.TRANSPORT.items()
        },
        "stt": _entries(data.STT),
        "llm": _entries(data.LLM),
        "tts": _entries(data.TTS),
        "realtime": _entries(data.REALTIME),
        "frameworks": _entries(data.FRAMEWORKS),
        "model": data.MODEL,
        "colors": data.COLORS,
    }


def to_json(indent: int = 2) -> str:
    return json.dumps(data_dict(), indent=indent, ensure_ascii=False)
