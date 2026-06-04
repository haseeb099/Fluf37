# Nexus AI Cursor Guide

## Project identity
Nexus AI is a multi-agent financial intelligence platform with:
- FastAPI backend
- Next.js frontend
- WebSocket streaming
- Vector memory
- Graph memory
- Time-series decision tracking
- Demo-first synthetic data mode

## Development principles
- Plan before coding.
- Keep changes small and isolated.
- Preserve streaming contracts.
- Validate all structured data.
- Prefer existing patterns in the repo.
- Do not introduce live integrations until the demo architecture is stable.

## Architecture priorities
1. Shared schemas and event contracts.
2. Backend agent orchestration.
3. WebSocket streaming.
4. Frontend dashboard consumption.
5. Memory and graph persistence.
6. Security, testing, and observability.

## Code quality rules
- Type everything.
- Use schema validation on all boundaries.
- Add tests for new logic.
- Avoid unnecessary rewrites.
- Keep functions small and readable.
- Maintain demo-mode compatibility.

## Working style
- Read the relevant TRD/PRD section before making changes.
- Draft a short implementation plan before coding.
- Update backend, frontend, and tests together when a contract changes.
- When uncertain, choose the simplest implementation that fits the architecture.
