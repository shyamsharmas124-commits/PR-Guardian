"""Local test simulator for PR Guardian.

Allows testing the secret scanner and AI reviewer locally without pushing to GitHub.
Usage:
    python scripts/test_local.py
    python scripts/test_local.py --file age.py
"""

import argparse
import json
import os
import sys

# Import review engine functions
sys.path.insert(0, os.path.dirname(__file__))
from review_pr import (
    SECRET_PATTERNS,
    ask_ai,
    format_inline_comment,
    load_repository_guidelines,
    normalize_review,
    scan_diff_for_secrets,
)

SAMPLE_DIFF_DEFECT = """
diff --git a/age.py b/age.py
new file mode 100644
index 0000000..8331169
--- /dev/null
+++ b/age.py
@@ -0,0 +1,7 @@
+def is_adult(age: int) -> bool:
+    # Deliberate off-by-one bug: 18 should be an adult!
+    return age > 18
+
+def calculate_discount(price: float, discount: float) -> float:
+    return price - (price * discount)
"""

SAMPLE_DIFF_SECRET = """
diff --git a/config.py b/config.py
new file mode 100644
index 0000000..e69de29
--- /dev/null
+++ b/config.py
@@ -0,0 +1,3 @@
+# Leaked credential test
+AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
+DATABASE_URL = "postgres://admin:password@localhost:5432/db"
"""


def test_secret_scanner():
    print("=" * 60)
    print("TEST 1: Deterministic Secret Scanner")
    print("=" * 60)
    sample_files = [
        {"path": "config.py", "patch": SAMPLE_DIFF_SECRET}
    ]
    findings = scan_diff_for_secrets(sample_files, {"config.py": {1, 2, 3}})
    print(f"Detected {len(findings)} secret leaks:")
    for f in findings:
        print(f"  [{f['severity'].upper()}] Line {f['line']}: {f['title']}")
        print(f"  Explanation: {f['explanation']}")
    assert len(findings) > 0, "Secret scanner should have caught AWS_KEY"
    print("Secret scanner test passed!\n")


def test_ai_reviewer(groq_key: str | None = None, gemini_key: str | None = None):
    print("=" * 60)
    print("TEST 2: AI Review Engine (Groq / Gemini)")
    print("=" * 60)

    if groq_key:
        os.environ["GROQ_API_KEY"] = groq_key
    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key

    has_groq = bool(os.environ.get("GROQ_API_KEY"))
    has_gemini = bool(os.environ.get("GEMINI_API_KEY"))

    if not has_groq and not has_gemini:
        print("Note: Neither GROQ_API_KEY nor GEMINI_API_KEY set in environment.")
        print("Set one to run the live AI model test, e.g.:")
        print("  $env:GROQ_API_KEY='gsk_...' ; python scripts/test_local.py")
        print("  $env:GEMINI_API_KEY='AIza...' ; python scripts/test_local.py")
        return

    diff_files = [
        {
            "path": "age.py",
            "status": "added",
            "patch": SAMPLE_DIFF_DEFECT.strip(),
        }
    ]
    changed_lines = {"age.py": {1, 2, 3, 4, 5, 6, 7}}

    guidelines = load_repository_guidelines()
    try:
        data, provider, model = ask_ai(diff_files, guidelines)
        print(f"Provider: {provider} ({model})")
        print("Raw AI response:\n", json.dumps(data, indent=2))

        score, scores, risk, summary, findings, tests = normalize_review(data, changed_lines, [])
        print("\nNormalized Scorecard:")
        print(f"  Overall Score: {score}/100")
        print(f"  Risk: {risk.upper()}")
        print(f"  Category Scores: {scores}")
        print(f"  Actionable findings: {len(findings)}")
        for f in findings:
            print("\n" + format_inline_comment(f))
    except Exception as e:
        print(f"AI Review test error: {e}")


def main():
    parser = argparse.ArgumentParser(description="Test PR Guardian locally")
    parser.add_argument("--groq-key", help="Groq API key")
    parser.add_argument("--gemini-key", help="Gemini API key")
    args = parser.parse_args()

    test_secret_scanner()
    test_ai_reviewer(args.groq_key, args.gemini_key)


if __name__ == "__main__":
    main()
