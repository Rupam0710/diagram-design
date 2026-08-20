#!/usr/bin/env python3
# ruff: noqa: I001
"""Regression tests for docs links and routing-surface verification."""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parent.parent
VERIFY = ROOT / "scripts" / "verify-docs-sync.py"


def load_verify_module():
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("diagram_design_verify_docs", VERIFY)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load verify-docs-sync.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    verify = load_verify_module()
    with tempfile.TemporaryDirectory(prefix="verify-docs-sync-") as temp_dir:
        skill = pathlib.Path(temp_dir)
        references = skill / "references"
        references.mkdir()
        (references / "present.md").write_text("# Present\n", encoding="utf-8")

        errors: list[str] = []
        verify.check_skill_reference_links(
            errors,
            "See [present](references/present.md) and [section](references/present.md#part).",
            skill,
        )
        if errors:
            raise AssertionError(f"valid reference link failed: {errors}")

        errors = []
        verify.check_skill_reference_links(
            errors,
            "See [missing](references/missing.md).",
            skill,
        )
        expected = "SKILL.md links to missing reference 'references/missing.md'"
        if errors != [expected]:
            raise AssertionError(f"broken reference was not reported: {errors}")

        errors = []
        verify.check_skill_reference_links(
            errors,
            "See [README](../../README.md), [asset](assets/example.html), and https://example.com.",
            skill,
        )
        if errors:
            raise AssertionError(f"non-reference links should be ignored: {errors}")

        root = pathlib.Path(temp_dir) / "repo"
        profile_reference = root / "skills/diagram-design/references/profiles.md"
        doctor_reference = root / "skills/diagram-design/references/doctor.md"
        export_reference = root / "skills/diagram-design/references/export.md"
        drawio_reference = root / "skills/diagram-design/references/import-drawio.md"
        mermaid_reference = root / "skills/diagram-design/references/import-mermaid.md"
        export_command = root / "commands/export-diagram.md"
        drawio_command = root / "commands/import-drawio.md"
        mermaid_command = root / "commands/import-mermaid.md"
        profile_command = root / "commands/profile.md"
        profile_prompt = root / "prompts/profile.md"
        doctor_command = root / "commands/doctor.md"
        export_prompt = root / "prompts/export-diagram.md"
        mermaid_prompt = root / "prompts/import-mermaid.md"
        doctor_prompt = root / "prompts/doctor.md"
        for path in (
            profile_reference,
            doctor_reference,
            export_reference,
            drawio_reference,
            mermaid_reference,
            export_command,
            drawio_command,
            mermaid_command,
            profile_command,
            profile_prompt,
            doctor_command,
            export_prompt,
            mermaid_prompt,
            doctor_prompt,
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
        profile_reference.write_text("# Profiles\n", encoding="utf-8")
        doctor_reference.write_text("# Doctor\n", encoding="utf-8")
        export_reference.write_text("# Export\n", encoding="utf-8")
        drawio_reference.write_text("# Draw.io\n", encoding="utf-8")
        mermaid_reference.write_text("# Mermaid\n", encoding="utf-8")
        export_command.write_text("Follow references/export.md.\n", encoding="utf-8")
        drawio_command.write_text("Follow references/import-drawio.md.\n", encoding="utf-8")
        mermaid_command.write_text("Follow references/import-mermaid.md.\n", encoding="utf-8")
        profile_command.write_text("Follow references/profiles.md.\n", encoding="utf-8")
        profile_prompt.write_text("Follow references/profiles.md.\n", encoding="utf-8")
        doctor_command.write_text("Follow references/doctor.md.\n", encoding="utf-8")
        export_prompt.write_text("Follow references/export.md.\n", encoding="utf-8")
        mermaid_prompt.write_text("Follow references/import-mermaid.md.\n", encoding="utf-8")
        doctor_prompt.write_text("Follow references/doctor.md.\n", encoding="utf-8")

        errors = []
        verify.check_routing_surfaces(errors, root)
        if errors:
            raise AssertionError(f"valid routing surfaces failed: {errors}")

        doctor_prompt.unlink()
        errors = []
        verify.check_routing_surfaces(errors, root)
        expected = "routing surface is missing: prompts/doctor.md"
        if errors != [expected]:
            raise AssertionError(f"missing routing prompt was not reported: {errors}")

        doctor_prompt.write_text("Stale standalone instructions.\n", encoding="utf-8")
        errors = []
        verify.check_routing_surfaces(errors, root)
        expected = (
            "routing surface does not route to references/doctor.md: prompts/doctor.md"
        )
        if errors != [expected]:
            raise AssertionError(f"stale routing prompt was not reported: {errors}")

    print(
        "PASS: docs sync checks reference links and command/prompt routing parity"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
