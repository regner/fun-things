# Historical telemetry validity

This pre-review baseline remains evidence of its recorded gameplay outcome, but its proxy-stage
telemetry is **invalid**. The old proxy reused one timestamp taken before `recvfrom()` for receive
and forward, forcing same-poll zero-delay deliveries to report zero. Do not use
`proxy.jsonl`, `original-result.json` proxy delays, or `reanalyzed-result.json` as proxy-stage
evidence. Corrected receive/forward telemetry is under `../matrix-03-safe-proxy/`.
