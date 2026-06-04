---
name: test-hardening
description: Add tests and harden behavior
---

# Workflow
1. Find the narrowest failing behavior.
2. Write tests for success and edge cases.
3. Implement the minimal fix.
4. Re-run tests and typecheck.
5. Repeat until stable.

# Rules
- Avoid brittle tests.
- Use fixtures for demo data.
- Validate schema changes explicitly.
- Prefer regression tests for bugs.
