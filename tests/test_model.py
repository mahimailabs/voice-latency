from voice_latency import data, estimate
from voice_latency.export import data_dict


def test_default_cascaded_matches_website():
    e = estimate()
    assert e.total_p50 == 1326
    assert e.total_p95 == 1589
    assert len(e.rows) == 7
    assert e.max_hop == "endp"


def test_realtime_replaces_the_cascade():
    e = estimate(mode="realtime", realtime="OpenAI GPT Realtime")
    keys = {r.key for r in e.rows}
    assert "model" in keys
    assert not {"stt", "llm", "tts"} & keys
    assert e.total_p50 > 0


def test_framework_adds_an_overhead_hop():
    base = estimate()
    with_fw = estimate(framework="LiveKit Agents")
    assert any(r.key == "framework" for r in with_fw.rows)
    assert with_fw.total_p50 > base.total_p50


def test_semantic_turn_math():
    e = estimate(turn="semantic", endpointing=700)
    endp = next(r for r in e.rows if r.key == "endp")
    assert endp.p50 == 495  # 700 * 0.55 + 110


def test_every_entry_has_a_source_and_date():
    for group in (data.STT, data.LLM, data.TTS, data.REALTIME, data.FRAMEWORKS):
        for name, entry in group.items():
            assert entry.source, name
            assert entry.date is not None, name


def test_export_shape():
    d = data_dict()
    for k in ("transport", "stt", "llm", "tts", "realtime", "frameworks", "model", "colors", "version"):
        assert k in d
    assert d["stt"]["Deepgram Nova-3"]["p50"] == 90
    assert d["realtime"]["Gemini Live (Flash)"]["p95"] == 660
