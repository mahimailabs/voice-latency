"""Command line: estimate a budget, list providers, or export the dataset.

    voice-latency                              # default cascaded turn
    voice-latency --mode realtime --realtime "Gemini Live (Flash)"
    voice-latency --framework "LiveKit Agents" --transport WebRTC
    voice-latency list
    voice-latency export --out data.json
"""

from __future__ import annotations

import argparse
import sys

from . import __version__, data
from .export import to_json
from .model import estimate


def _list() -> None:
    groups = [
        ("Transport", data.TRANSPORT),
        ("STT", data.STT),
        ("LLM", data.LLM),
        ("TTS", data.TTS),
        ("Realtime (speech-to-speech)", data.REALTIME),
        ("Frameworks", data.FRAMEWORKS),
    ]
    for title, d in groups:
        print(f"\n{title}")
        for name in d:
            print(f"  - {name}")


def _print_estimate(args: argparse.Namespace) -> None:
    est = estimate(
        mode=args.mode,
        transport=args.transport,
        stt=args.stt,
        llm=args.llm,
        tts=args.tts,
        realtime=args.realtime,
        framework=args.framework,
        same_region=not args.cross_region,
        turn=args.turn,
        endpointing=args.endpointing,
        calls=args.calls,
    )
    label = "realtime" if args.mode == "realtime" else "cascaded"
    print(f"\nVoice agent turn latency  ({label}, {args.transport})\n")
    print(f"  {'Hop':<28}{'p50':>8}{'p95':>8}{'share':>9}")
    print("  " + "-" * 53)
    for h in est.rows:
        print(f"  {h.label:<28}{h.p50:>6}ms{h.p95:>6}ms{h.share(est.total_p50):>8.1f}%")
    print("  " + "-" * 53)
    print(f"  {'TOTAL':<28}{est.total_p50:>6}ms{est.total_p95:>6}ms")
    print(f"\n  {est.verdict}\n")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="voice-latency", description="Per-hop latency budget for voice agents.")
    p.add_argument("--version", action="version", version=f"voice-latency {__version__}")
    p.add_argument("command", nargs="?", default="estimate", choices=["estimate", "list", "export"])
    p.add_argument("--mode", default="cascaded", choices=["cascaded", "realtime"])
    p.add_argument("--transport", default="PSTN / SIP", choices=list(data.TRANSPORT))
    p.add_argument("--stt", default="Deepgram Nova-3", choices=list(data.STT))
    p.add_argument("--llm", default="GPT-4o mini", choices=list(data.LLM))
    p.add_argument("--tts", default="Cartesia Sonic", choices=list(data.TTS))
    p.add_argument("--realtime", default="OpenAI GPT Realtime", choices=list(data.REALTIME))
    p.add_argument("--framework", default="None (raw)", choices=list(data.FRAMEWORKS))
    p.add_argument("--turn", default="silence", choices=["silence", "semantic"])
    p.add_argument("--endpointing", type=int, default=700)
    p.add_argument("--calls", type=int, default=25)
    p.add_argument("--cross-region", action="store_true", help="inference in a different region than users")
    p.add_argument("--out", default="-", help="export target ('-' for stdout)")
    args = p.parse_args(argv)

    if args.command == "list":
        _list()
    elif args.command == "export":
        text = to_json()
        if args.out == "-":
            print(text)
        else:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(text + "\n")
            print(f"wrote {args.out}", file=sys.stderr)
    else:
        _print_estimate(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
