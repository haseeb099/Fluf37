---
name: agent-builder
description: Build or refactor a Nexus agent end-to-end
---

# Use when
Use for Connector, Silent Finder, Red Team, Traceback, Decision, or Evolution agent work.

# Workflow
1. Read the TRD and PRD section for the target agent.
2. Identify inputs, outputs, dependencies, and streaming events.
3. Update backend code.
4. Add or update tests.
5. Verify frontend compatibility.
6. Confirm demo mode still works.

# Output requirements
- Typed Pydantic models.
- Clear structured logging.
- Async-compatible code.
- Tests for success and failure paths.
