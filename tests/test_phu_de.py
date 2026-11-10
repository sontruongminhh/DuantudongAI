"""Phụ đề không cắt số thập phân thành hai dòng."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "engine"))
from ai_film_studio import split_caption  # noqa: E402


def test_decimal_stays_on_one_line():
    for text in ["いまの物価に直すと、およそ1.5兆円です。", "三菱は8.3%、住友は5.1%でした。", "ふだんの切符は11.9%上がりました。"]:
        chunks = split_caption(text, 20, "ja")
        assert not any(c.endswith(".") for c in chunks), chunks
        assert "".join(chunks) == text


def test_sentence_end_still_splits():
    assert split_caption("It ends. Next one starts here.", 45, "en") == ["It ends.", "Next one starts here."]
