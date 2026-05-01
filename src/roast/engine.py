"""Roast engine — generates code reviews from a brutally honest senior engineer."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


FALLBACK_ROASTS = [
    "This code works, which is the nicest thing I can say about it.",
    "I have seen worse. Not much worse, but some worse.",
    "The variable names suggest someone learned to code from a single Stack Overflow answer.",
    "This is held together with string literals and good intentions.",
    "Future you will open this file and immediately close the laptop.",
    "The comments explain what the code does. They do not explain why. Nobody knows why.",
    "Every line here is a decision. Not all decisions were good decisions.",
]


@dataclass
class RoastResult:
    """Result of a code roast."""
    language: str
    line_count: int
    roast: str
    specific_issues: list[str] = field(default_factory=list)
    score: str = "unrated"
    verdict: str = ""

    @property
    def has_issues(self) -> bool:
        return len(self.specific_issues) > 0


def roast_code(code: str, language: str = "unknown", mercy: bool = False) -> RoastResult:
    """Submit code for roasting. Returns a RoastResult."""
    lines = code.strip().splitlines()
    line_count = len(lines)
    api_key = os.environ.get("OPENROUTER_API_KEY", "")

    if api_key:
        return _ai_roast(code, language, line_count, mercy, api_key)
    return _rule_roast(code, language, line_count, mercy)


def _ai_roast(code: str, language: str, line_count: int, mercy: bool, api_key: str) -> RoastResult:
    try:
        from openai import OpenAI
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

        tone = "constructive but honest" if mercy else "brutally honest, funny, and savage but never mean-spirited"
        prompt = f"""You are a senior engineer with 20 years of experience who has seen every possible way to write bad code. You are reviewing the following {language} code.

Your tone is {tone}. You find specific problems, explain why they are problems, and suggest fixes. You are funny. You have opinions. You have been hurt before.

Code to review ({line_count} lines):
```{language}
{code[:3000]}
```

Respond in EXACTLY this format:
ISSUES: <3-5 specific issues, each on its own line starting with "- ">
ROAST: <one overall roast paragraph, 2-4 sentences, funny and specific>
SCORE: <a made-up score like "4/10 - will haunt your dreams" or "7/10 - disappointing but salvageable">
VERDICT: <one final sentence, the kind a senior engineer mutters while closing the PR>"""

        response = client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct:free",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        return _parse_roast_response(response.choices[0].message.content, language, line_count)
    except Exception:
        return _rule_roast(code, language, line_count, mercy)


def _parse_roast_response(text: str, language: str, line_count: int) -> RoastResult:
    sections: dict[str, str] = {}
    current = ""
    for line in text.strip().splitlines():
        for key in ("ISSUES", "ROAST", "SCORE", "VERDICT"):
            if line.startswith(f"{key}:"):
                current = key
                sections[key] = line[len(key)+1:].strip()
                break
        else:
            if current and current in sections:
                sections[current] += "\n" + line

    issues = [l.lstrip("- ").strip() for l in sections.get("ISSUES", "").splitlines() if l.strip().startswith("-")]

    return RoastResult(
        language=language,
        line_count=line_count,
        roast=sections.get("ROAST", FALLBACK_ROASTS[line_count % len(FALLBACK_ROASTS)]),
        specific_issues=issues,
        score=sections.get("SCORE", "unrated"),
        verdict=sections.get("VERDICT", ""),
    )


def _rule_roast(code: str, language: str, line_count: int, mercy: bool) -> RoastResult:
    """Rule-based roast without LLM."""
    issues = []
    code_lower = code.lower()

    if "except:" in code or "except exception:" in code_lower:
        issues.append("Bare except clause detected — somewhere something is silently failing and you will find out at 2am")
    if "TODO" in code or "FIXME" in code or "HACK" in code:
        count = code.count("TODO") + code.count("FIXME") + code.count("HACK")
        issues.append(f"{count} TODO/FIXME/HACK comment(s) — future you is already disappointed")
    if "password" in code_lower or "secret" in code_lower or "api_key" in code_lower:
        issues.append("Possible hardcoded credential — please don't do this to yourself")
    if code_lower.count("def ") > 10:
        issues.append(f"{code_lower.count('def ')} functions in one file — this is a file, not a novel")
    if "sleep(" in code_lower:
        issues.append("time.sleep() detected — someone is waiting for something and hoping for the best")
    if not issues:
        issues.append("No obvious disasters found — suspiciously clean, keep an eye on this one")

    roast = FALLBACK_ROASTS[line_count % len(FALLBACK_ROASTS)]
    if mercy:
        roast = "This is fine. Not great. Not terrible. Fine."

    score_num = max(1, min(9, 10 - len(issues) * 2))
    descriptors = ["career-defining mistake", "needs prayer", "concerning", "mediocre", "acceptable",
                   "not bad", "pretty good", "solid", "impressive", "chef's kiss"]
    score = f"{score_num}/10 — {descriptors[score_num - 1]}"

    return RoastResult(
        language=language,
        line_count=line_count,
        roast=roast,
        specific_issues=issues,
        score=score,
        verdict="Approved with comments. Many, many comments.",
    )