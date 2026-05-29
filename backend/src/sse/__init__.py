"""Server-Sent Events infrastructure for live intelligence streaming.

Manages per-deployment subscriptions and broadcasts typed SSE events
(signal, entity, relationship, insight, node_start, node_complete, complete)
to connected frontend clients.
"""

