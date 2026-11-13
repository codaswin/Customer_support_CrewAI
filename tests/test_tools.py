import tools
from tools import log_gap


def test_kb_finds_in_doc_and_rejects_off_topic():
    import kb
    kb.ingest()
    assert "30 days" in kb.search("How long do I have to return coffee?")
    assert kb.search("Who won the 2018 football world cup?") == "NOT_FOUND"


def test_log_gap_writes_timestamped_line(tmp_path, monkeypatch):
    monkeypatch.setattr(tools, "LOG_FILE", tmp_path / "log.txt")
    log_gap.run(query="do you sell gift cards?", web_searched=True)
    log_gap.run(query="ignored", web_searched=False)
    lines = (tmp_path / "log.txt").read_text().splitlines()
    assert len(lines) == 1 and lines[0].endswith("| do you sell gift cards?")
