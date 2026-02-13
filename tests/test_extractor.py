from extractor import extract_tags, normalize_todo_to_markdown


def test_normalize_todo_to_markdown():
    text = "提出する。睡眠を整える\n・遅刻しない-計画を立てる 1.復習する"
    result = normalize_todo_to_markdown(text)
    assert "- 提出する" in result
    assert "- 睡眠を整える" in result
    assert "- 遅刻しない" in result


def test_extract_tags_unique_sorted():
    tags = extract_tags("欠席あり", "睡眠不足", "提出遅れ")
    assert tags == ["提出", "欠席", "睡眠"]
