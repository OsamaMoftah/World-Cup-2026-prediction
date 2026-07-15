from pathlib import Path


def test_result_workflow_has_keyless_fallback():
    workflow = Path(".github/workflows/result-check.yml").read_text(
        encoding="utf-8"
    )

    assert "--provider auto" in workflow
    assert "FOOTBALL_DATA_API_KEY is not configured" not in workflow
    assert "provider=" in workflow


def test_result_workflow_keeps_human_review_gate():
    workflow = Path(".github/workflows/result-check.yml").read_text(
        encoding="utf-8"
    )

    assert "peter-evans/create-pull-request" in workflow
    assert "--allow-corrections" in workflow
    assert "health_check.py --ignore-overdue-results" in workflow
