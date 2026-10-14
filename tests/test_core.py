import json

import pytest

from tool_pair_check.core import InvalidTrace, validate_text


def kinds(text):
    return validate_text(text)


def test_empty_interleaved_and_out_of_order_distinct_ids_are_valid():
    assert kinds("") == {"status": "valid", "record_count": 0, "findings": []}
    assert kinds('{"id":"a","type":"call"}\n{"id":"b","type":"result"}\n'
                 '{"id":"b","type":"call"}\n{"id":"a","type":"result"}') ["status"] == "violations"
    assert kinds('{"id":"a","type":"call"}\n{"id":"b","type":"call"}\n'
                 '{"id":"b","type":"result"}\n{"id":"a","type":"result"}') ["status"] == "valid"


def test_result_before_call_orphan_and_later_result_satisfies_call():
    report = kinds('{"id":"x","type":"result"}\n{"id":"x","type":"call"}')
    assert report["findings"] == [{"line": 1, "kind": "orphan_result"},
                                   {"line": 2, "kind": "missing_result"}]
    report = kinds('{"id":"x","type":"result"}\n{"id":"x","type":"call"}\n'
                   '{"id":"x","type":"result"}')
    assert report["findings"] == [{"line": 1, "kind": "orphan_result"},
                                   {"line": 3, "kind": "duplicate_result"}]


def test_duplicate_calls_do_not_create_multiple_missing_requirements():
    report = kinds('{"id":"x","type":"call"}\n{"id":"x","type":"call"}')
    assert report["findings"] == [{"line": 1, "kind": "missing_result"},
                                   {"line": 2, "kind": "duplicate_call"}]


def test_duplicate_combination_and_sorting():
    report = kinds('\n'.join(['{"id":"x","type":"result"}',
                               '{"id":"x","type":"result"}',
                               '{"id":"x","type":"call"}',
                               '{"id":"x","type":"call"}']))
    assert report["findings"] == [
        {"line": 1, "kind": "orphan_result"},
        {"line": 2, "kind": "duplicate_result"},
        {"line": 2, "kind": "orphan_result"},
        {"line": 3, "kind": "missing_result"},
        {"line": 4, "kind": "duplicate_call"},
    ]


def test_unicode_exact_id_and_cr_lf_crlf():
    assert kinds('{"id":"é","type":"call"}\r{"id":"é","type":"result"}') ["findings"]
    assert kinds('{"id":"雪","type":"call"}\r\n{"id":"雪","type":"result"}') ["status"] == "valid"


@pytest.mark.parametrize("text", [
    "\n", "{}", '{"id":"x","type":"call","extra":1}',
    '{"id":"","type":"call"}', '{"id":1,"type":"call"}',
    '{"id":"x","type":"other"}', '{"id":"x","type":"call","id":"y"}',
    '{"id":"x","type":"call"}\nnot json', '{"id":"x","type":"call"}\n\n',
    '{"id":"x","type":"call","n":NaN}', '{"id":"x","type":"call"}\u2028',
])
def test_strict_rejects_entire_input(text):
    with pytest.raises(InvalidTrace):
        validate_text(text)


def test_surrogate_escape_is_parsed_but_report_never_contains_id():
    report = kinds('{"id":"secret\\ud800","type":"call"}')
    assert "secret" not in json.dumps(report)
