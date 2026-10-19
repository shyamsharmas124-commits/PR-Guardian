# PR Guardian — Repository Review Guidelines

PR Guardian loads and applies these guidelines during every automated review.

## Architecture & Code Standards
1. **Clean Code & Modularity**: Keep functions focused on a single responsibility. Avoid giant multi-hundred line functions.
2. **Error Handling**: Never use bare `except:` or swallow exceptions silently without logging or re-raising.
3. **Type Hinting**: Prefer Python type annotations for function signatures where applicable.
4. **Security & Data Sanitization**:
   - Always validate external and user input.
   - Never hardcode secrets, tokens, or API credentials into source code or test files.
   - Prevent SQL injection, command injection, and SSRF vulnerabilities.
5. **Testing**:
   - Critical business logic and edge cases should have unit tests.
   - Handle off-by-one errors and null/None edge cases.
