# Kosciuszko: High-Altitude ASX Data Pipeline

**Kosciuszko** is a resilient, precision-engineered data ingestion and technical analysis pipeline for the Australian Securities Exchange (ASX). Named after Australia's highest peak, the system is designed to provide a "summit view" of market data, ensuring stability and accuracy even within the strict resource constraints of free-tier cloud infrastructure.

## 1. System Philosophy: "Thin Edge, Thick Core"

Kosciuszko follows a specialized architecture designed for **OCI VM Micro (1GB RAM)** environments:

- **Python (The Ascent)**: A lightweight, stateless ingestion layer running on the **Ironbark** VM, optimized for low-memory footprints and efficient web scraping.
- **Oracle PL/SQL (The Summit)**: Heavy-duty technical indicator calculations, including EMA, PSAR, and Supertrend, are offloaded to the **GoldenWattle** database, leveraging Oracle's native processing power to prevent VM memory exhaustion.

## 2. Infrastructure Code Names

- **Compute Instance**: `Ironbark` (OCI Ubuntu Micro - 1/8 OCPU / 1GB RAM)
- **Database Instance**: `GoldenWattle` (Oracle Autonomous Database - Always Free)
- **Monitoring**: Pushover API integration for real-time "Basecamp" status reports.

## 3. Key Features

### 3.1 Multi-Pass Resilience Strategy

To guarantee data integrity despite network instability or OOM (Out-of-Memory) risks, the system employs a three-pass mechanism:

1. **Initial Sweep**: Bulk ingestion of the targeted ticker list.
2. **Recovery Passes**: Automatic identification of gaps via the `VW_MISSING_SYMBOLS` database view, followed by targeted re-scraping.

### 3.2 Engineered for 1GB RAM

- **Singleton Connection Management**: Prevents overhead by maintaining a single, global database pool.
- **Chunked Data Streaming**: Processes and commits data in small batches of 5-10 symbols to keep the memory profile flat.
- **Process Shielding**: Automated cleanup scripts, including `pkill`, ensure no zombie Chrome or Driver processes survive between sessions.

## 4. Project Structure

```text
/kosciuszko
├── src/                # Python ingestion layer
│   ├── scrapers/       # Yahoo Finance, AFR, Shortman, etc.
│   ├── main.py         # Task orchestration and multi-pass logic
│   ├── db_operator.py  # Singleton Oracle manager
│   └── config.py       # Environment and safety validation
├── sql/                # GoldenWattle database layer
│   ├── tables/         # ODS (raw) and FTR (indicator) DDL
│   ├── views/          # Logic for recovery and debugging
│   └── procedures/     # PL/SQL technical analysis engines
├── scripts/            # Operational automation for cron and cleanup
├── tests/              # TDD suite powered by pytest
└── docs/               # Technical specifications and research
```

## 5. Deployment and Execution

### 5.1 Prerequisites

- Python 3.10+
- Oracle Instant Client and Oracle Wallet, configured in `config/`
- `chromium-browser` and `chromedriver` for headless scraping

### 5.2 Installation

1. Clone the repository to the `Ironbark` instance.
2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create `config/.env` based on `config/.env.example`.

### 5.3 Running Tests

Execute the TDD suite to ensure infrastructure readiness:

```bash
pytest tests/
```

## 6. Execution Windows (AEST)

- **Session Alpha (15:25)**: Pre-close ingestion for early signal detection.
- **Session Omega (17:00)**: Post-close finalization and technical indicator recalculation.

---

Kosciuszko - reaching the peak of market intelligence through engineering resilience.
