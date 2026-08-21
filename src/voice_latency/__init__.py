"""voice-latency: a per-hop latency budget for voice agents.

Cascaded (STT + LLM + TTS) and realtime (speech-to-speech) architectures, plus
framework overhead. The numbers live in ``voice_latency.data`` and are the whole
point: PR better ones. See ``estimate`` for the model.
"""

from . import data
from .model import Estimate, Hop, estimate, verdict

__version__ = "0.1.1"
__all__ = ["estimate", "Estimate", "Hop", "verdict", "data", "__version__"]
