#!/usr/bin/env python3
"""Record a local portrait-consent preflight.

The checks restate public LiveFaceSwapVideo rules so an operator can write
down their own answers before using the service. This program does not open
a network connection, upload a portrait, call an API, or decide that a
session is lawful.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path


CHECKS: tuple[dict[str, str], ...] = (
    {
        "id": "adult_operator",
        "statement": "The person operating the product is 18 or older.",
        "source": "https://livefaceswap.video/terms",
    },
    {
        "id": "likeness_permission",
        "statement": (
            "Every identifiable face is the operator's own, or that person "
            "has given clear, informed, voluntary, and demonstrable consent "
            "for AI processing and derivative output. A public, social, news, "
            "street, screenshot, or old private photo is not that consent."
        ),
        "source": "https://livefaceswap.video/acceptable-use",
    },
    {
        "id": "no_minor",
        "statement": (
            "The reference and the live scene do not depict anyone under 18, "
            "including a person who appears to be under 18."
        ),
        "source": "https://livefaceswap.video/acceptable-use",
    },
    {
        "id": "no_public_figure_without_authorization",
        "statement": (
            "The reference is not a celebrity or other public figure unless "
            "the operator is that person and can show sufficient authorization. "
            "Deceased public figures remain restricted where their rights survive."
        ),
        "source": "https://livefaceswap.video/terms",
    },
    {
        "id": "permitted_purpose",
        "statement": (
            "The intended use is lawful creative or entertainment use, and it "
            "is not impersonation, fraud, identity-check evasion, harassment, "
            "sexual or non-consensual intimate imagery, political deception, "
            "or another use banned by the acceptable-use policy."
        ),
        "source": "https://livefaceswap.video/acceptable-use",
    },
    {
        "id": "synthetic_disclosure",
        "statement": (
            "If the output is shared where someone could mistake it for a real "
            "recording, it will be disclosed as AI-generated, and any disclosure "
            "applied by the service will be left in place."
        ),
        "source": "https://livefaceswap.video/terms",
    },
)

CHECK_IDS = tuple(item["id"] for item in CHECKS)


class AnswerError(ValueError):
    """The answer file is not a complete boolean checklist."""


@dataclass(frozen=True)
class CheckResult:
    id: str
    statement: str
    source: str
    acknowledged: bool


@dataclass(frozen=True)
class PreflightResult:
    checks: tuple[CheckResult, ...]

    @property
    def ready(self) -> bool:
        return all(item.acknowledged for item in self.checks)

    @property
    def blocking(self) -> tuple[CheckResult, ...]:
        return tuple(item for item in self.checks if not item.acknowledged)


def evaluate(answers: dict[str, object]) -> PreflightResult:
    """Return one result per published check.

    Every known id must be present and boolean. Unknown ids are rejected so
    a typo cannot silently pass.
    """

    if not isinstance(answers, dict):
        raise AnswerError("answers must be a JSON object")

    unknown = sorted(set(answers) - set(CHECK_IDS))
    if unknown:
        raise AnswerError("unknown answer id: " + ", ".join(unknown))

    results: list[CheckResult] = []
    for item in CHECKS:
        value = answers.get(item["id"])
        if not isinstance(value, bool):
            raise AnswerError(f"{item['id']} must be true or false")
        results.append(
            CheckResult(
                id=item["id"],
                statement=item["statement"],
                source=item["source"],
                acknowledged=value,
            )
        )
    return PreflightResult(tuple(results))


def load_answers(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise AnswerError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise AnswerError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise AnswerError("answers must be a JSON object")
    return payload


def format_report(result: PreflightResult) -> str:
    lines = [
        "LiveFaceSwapVideo local portrait-consent preflight",
        "This records the operator's answers on this computer.",
        "It does not contact the service or approve a live session.",
        "",
    ]
    for item in result.checks:
        mark = "ACKNOWLEDGED" if item.acknowledged else "BLOCKING"
        lines.append(f"[{mark}] {item.id}")
        lines.append(f"  {item.statement}")
        lines.append(f"  source: {item.source}")
    lines.append("")
    if result.ready:
        lines.append(
            "Result: ready as a local record. This is not permission from "
            "the person in the portrait and it is not approval by LiveFaceSwapVideo."
        )
    else:
        blocked = ", ".join(item.id for item in result.blocking)
        lines.append(f"Result: not ready. Blocking: {blocked}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check a local JSON file of portrait-consent answers. "
            "No network access."
        )
    )
    parser.add_argument(
        "answers",
        type=Path,
        help="JSON object whose keys are the check ids and whose values are booleans",
    )
    args = parser.parse_args(argv)
    try:
        result = evaluate(load_answers(args.answers))
    except AnswerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(format_report(result), end="")
    return 0 if result.ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
