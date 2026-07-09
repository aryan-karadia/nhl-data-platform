# NHL Analytics Data Platform 🏒

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Apache Spark](https://img.shields.io/badge/PySpark-Data_Processing-orange.svg)](https://spark.apache.org/)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF.svg)](https://github.com/features/actions)
[![Data Lake](https://img.shields.io/badge/Data_Lake-Cloudflare_R2-F38020.svg)](https://www.cloudflare.com/developer-platform/r2/)
[![Data Warehouse](https://img.shields.io/badge/Data_Warehouse-MotherDuck-FFD966.svg)](https://motherduck.com/)

## 📖 Overview
An end-to-end, zero-cost, near-real-time data platform designed to ingest, process, and serve NHL telemetry and metadata. This pipeline extracts raw JSON from the public NHL API, orchestrates processing via automated CI/CD workflows, transforms nested structures using PySpark, and loads optimized data into a serverless cloud warehouse. 

This backend acts as the data engine for the [NHL Stat Tracker](https://nhl-stat-tracker.vercel.app/) frontend.

## 🏗️ System Architecture
The pipeline follows a modern ELT (Extract, Load, Transform) architecture:
1. **Extract:** Python scripts pull live game states, player stats, and play-by-play telemetry from the NHL API.
2. **Load (Data Lake):** Raw JSON payloads are pushed directly to a Cloudflare R2 (S3-compatible) object storage bucket.
3. **Transform:** PySpark processes the raw data, utilizing highly efficient, vectorized operations to flatten nested JSON structures into a relational star schema.
4. **Serve (Data Warehouse):** Transformed data is loaded into MotherDuck (Cloud DuckDB) for sub-100ms analytical querying by the frontend.
5. **Orchestration:** The entire workflow is fully automated via GitHub Actions cron schedules.

## 🚀 Engineering Highlights
* **Zero-Cost Scalability:** Architected using a 100% serverless, free-tier modern data stack with zero infrastructure management overhead.
* **Vectorized Processing:** Prioritizes vectorized transformations over loops, ensuring high-throughput data cleaning and metadata generation.
* **Automated Data Quality:** Integrated PyTest framework ensures data integrity and validates API payloads before they enter the data lake.
* **Decoupled Architecture:** Strict separation between the API ingestion layer, the object storage layer, and the analytical warehouse.

## 💻 Tech Stack
* **Language:** Python
* **Data Processing:** PySpark, Pandas/NumPy
* **Storage / Warehouse:** Cloudflare R2 (S3 API), MotherDuck
* **Orchestration & CI/CD:** GitHub Actions
* **Testing:** PyTest

## 🛠️ Local Development Setup
1. Clone the repository: `git clone https://github.com/aryan-karadia/nhl-data-platform.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Configure `.env` file with your Cloudflare R2 and MotherDuck credentials.
4. Run tests: `pytest tests/`
5. Execute manual pipeline run: `python src/main.py`