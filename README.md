# PR Guardian — free-first AI pull request reviewer

PR Guardian is a small GitHub Actions MVP. On same-repository pull requests, it sends textual PR diffs to a Groq model, posts an overall review plus inline comments on changed lines, and fails its required status check when the AI reports high-confidence high/critical issues, a score below 80, or high risk.

It does **not** run arbitrary code from the pull request. It only reads diffs and sends them to the configured AI provider. For the first version, PRs from forks are deliberately skipped so the Groq key is not expected to be available to untrusted contributors.

## Requirements

- A GitHub repository (public is easiest for a zero-cost demo).
- A Groq API key that is within the provider's current free-plan limits.
- GitHub Actions enabled.

## Setup

1. Copy `.github/workflows/pr-guardian.yml`, `scripts/review_pr.py`, and `requirements.txt` into the root of your repository.
2. In the repository, open **Settings → Secrets and variables → Actions → New repository secret**. Name it `GROQ_API_KEY` and paste your key.
3. Optional: under **Settings → Secrets and variables → Actions → Variables**, create `GROQ_MODEL` with a model currently available to your Groq account. The default is `openai/gpt-oss-20b`.
4. Commit these files to the default branch.
5. Create a new branch in the same repository, add a deliberately small test change, and open a pull request.
6. Open the PR's **Actions** tab and inspect the **PR Guardian** run. The bot should post a review summary and inline comments on eligible added lines.

## Merge behavior

- Quality gate fails if any valid, changed-line finding is high/critical with at least 80% model confidence, the score is below 80, or overall risk is marked high.
- A passing score does not mean the code is proven safe. Keep your unit tests, lint, security checks, required human reviews, and branch protection enabled.
- Auto-merge is **off by default**. Only after testing, enable **Settings → General → Pull Requests → Allow auto-merge**, configure branch protection/rulesets to require the PR Guardian check plus your real CI checks and required review(s), and add the Actions variable `ENABLE_AUTO_MERGE=true`.
- With auto-merge enabled, PR Guardian only asks GitHub to enable native auto-merge when the score is at least 85, risk is low, and no validated high/critical finding has at least 80% confidence. GitHub should still wait for its configured requirements. Do not enable this on a repository without proper protections.

## Security and limitations

- This starter intentionally uses `pull_request`, not `pull_request_target`, and skips fork PRs. Do not change it to `pull_request_target` while checking out or executing untrusted PR code.
- Keep API keys in GitHub Actions secrets. Do not commit `.env` files or credentials.
- Only changed lines that GitHub includes in a textual diff are eligible for inline comments. Binary files, oversized files, and missing patches may not be reviewed by this MVP.
- Free AI quotas can run out or change. An API/quota error fails the workflow, which may block merges if the workflow is a required check.
- AI findings can be wrong. Tune thresholds only after testing against examples of both real bugs and harmless changes.
- The first version reviews the diff only; it does not run tests, install project dependencies, or understand the full repository architecture.

## Local syntax check

```bash
python -m pip install -r requirements.txt
python -m py_compile scripts/review_pr.py
```

## Helpful official documentation

- GitHub Actions and `GITHUB_TOKEN`: https://docs.github.com/en/actions/tutorials/authenticate-with-github_token
- Create pull-request reviews and inline comments: https://docs.github.com/en/rest/pulls/reviews
- Fork PR security: https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target
- GitHub auto-merge: https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/automatically-merging-a-pull-request
- Groq Quickstart: https://console.groq.com/docs/quickstart
- Groq rate limits: https://console.groq.com/docs/rate-limits
