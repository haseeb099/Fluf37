---
name: websocket-feature
description: Add or update a WebSocket streaming feature
---

# Workflow
1. Define the event schema.
2. Implement backend event emission.
3. Update frontend parsing.
4. Update UI state handling.
5. Test reconnect, partial stream, and error states.

# Rules
- Maintain event order.
- Validate all payloads.
- Keep client and server contracts aligned.
- Preserve compatibility when possible.
