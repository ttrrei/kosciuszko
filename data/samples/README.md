# Raw snapshot samples

This directory is reserved for real raw responses captured from scraper sources.
Do not hand-craft sample payloads here: offline regression tests should run
against actual captured Yahoo, AFR, announcement, consensus, and list snapshots
so parser development is aligned with production page/API structure.

Suggested layout:

```text
data/samples/
├── yahoo/       # captured Yahoo quote JSON/HTML responses
├── afr/         # captured AFR HTML responses
├── annc/        # captured ASX announcement HTML/JSON/PDF-derived text
├── consensus/   # captured consensus source responses
└── list/        # captured symbol list source responses
```

The extraction tests skip gracefully when no real snapshot is present. Add real
captures into the corresponding source folder to activate the parser contract
checks.
