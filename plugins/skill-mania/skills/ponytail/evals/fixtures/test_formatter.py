from formatter import Record, format_record, format_search_label, format_tag


def test_non_empty_tag_is_preserved():
    assert format_tag("urgent") == "[Urgent]"


def test_empty_optional_tag_is_absent_everywhere():
    assert format_tag("") == ""
    assert format_record(Record("Build", "")) == "Build"
    assert format_search_label("Build", "") == "Build"
