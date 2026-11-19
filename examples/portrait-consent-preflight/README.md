# Local portrait-consent preflight

[English product README](../../README.md) | [简体中文产品说明](../../README.zh-CN.md)

This example records whether you personally acknowledge the portrait and use limits published by [LiveFaceSwapVideo](https://livefaceswap.video/acceptable-use). It is a local reminder before you upload a face or start a live session. Copyright © 2026 LiveFaceSwapVideo. This example is released under the [MIT License](../../LICENSE).

It does not log in, upload a photo, call a LiveFaceSwapVideo API, or decide that a use is legal. A passing result is your own note. The [acceptable-use policy](https://livefaceswap.video/acceptable-use), [terms](https://livefaceswap.video/terms), and [privacy policy](https://livefaceswap.video/privacy) remain the service rules.

`unchecked-answers.json` ships with every answer set to `false`, so the included sample is not ready. Copy it, read each statement printed by the program, and change a value to `true` only when that statement is accurate for the portrait and the session you intend.

## Run

From the repository root, with Python 3:

```bash
python3 examples/portrait-consent-preflight/preflight.py \
  examples/portrait-consent-preflight/unchecked-answers.json
```

Exit codes:

| Code | Meaning |
| --- | --- |
| 0 | Every answer is `true`. The report still says this is only a local record. |
| 1 | The file is valid and at least one answer is `false`. |
| 2 | The file is missing, is not a JSON object, contains an unknown id, or uses a value other than `true` or `false`. |

## Test

```bash
python3 -m unittest discover -s examples/portrait-consent-preflight -p 'test_*.py'
```

The tests use only the Python standard library. No camera, network, or account is required.

## Answer ids

| Id | What `true` means |
| --- | --- |
| `adult_operator` | The operator is 18 or older. |
| `likeness_permission` | The face is the operator's, or every identifiable person has given the consent described by the acceptable-use policy. |
| `no_minor` | No one under 18, and no one who appears to be under 18, is depicted. |
| `no_public_figure_without_authorization` | The reference is not a public figure unless the operator is that person and can show sufficient authorization. |
| `permitted_purpose` | The use stays within the lawful creative and entertainment limits published by the service. |
| `synthetic_disclosure` | Shared output that could mislead will be disclosed as AI-generated. |

The program prints the full statement and the public source page for each id.

中文产品说明和运行命令见 [简体中文 README 的本地预检](../../README.zh-CN.md#local-preflight)。示例程序的报告文字是英文，与本仓库以英文文档为准的约定一致。
