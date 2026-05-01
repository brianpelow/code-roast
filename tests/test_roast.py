"""Tests for code-roast engine."""

from roast.engine import roast_code, _rule_roast, RoastResult


def test_roast_returns_result() -> None:
    result = roast_code("def hello(): pass", "python")
    assert isinstance(result, RoastResult)
    assert result.language == "python"
    assert result.line_count == 1


def test_bare_except_detected() -> None:
    code = "try:\n    pass\nexcept:\n    pass"
    result = _rule_roast(code, "python", 4, False)
    assert any("except" in i.lower() for i in result.specific_issues)


def test_todo_detected() -> None:
    code = "# TODO: fix this\n# FIXME: and this\ndef f(): pass"
    result = _rule_roast(code, "python", 3, False)
    assert any("TODO" in i or "FIXME" in i for i in result.specific_issues)


def test_hardcoded_secret_detected() -> None:
    code = 'api_key = "sk-super-secret-12345"'
    result = _rule_roast(code, "python", 1, False)
    assert any("credential" in i.lower() or "password" in i.lower() or "secret" in i.lower()
               for i in result.specific_issues)


def test_mercy_mode_softer() -> None:
    code = "def f(): pass"
    result = _rule_roast(code, "python", 1, mercy=True)
    assert "fine" in result.roast.lower()


def test_score_format() -> None:
    result = roast_code("x = 1", "python")
    assert "/" in result.score


def test_has_issues_property() -> None:
    result = _rule_roast("try:\n    pass\nexcept:\n    pass", "python", 4, False)
    assert result.has_issues is True


def test_clean_code_gets_issue() -> None:
    result = _rule_roast("def greet(name: str) -> str:\n    return f'Hello {name}'", "python", 2, False)
    assert len(result.specific_issues) > 0