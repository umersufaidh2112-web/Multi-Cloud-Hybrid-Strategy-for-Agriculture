# 🌾 Multi-Cloud Hybrid Strategy for Agriculture

<div align="center">

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![AWS S3](https://img.shields.io/badge/AWS_S3-Free_Tier-FF9900?style=for-the-badge&logo=amazons3&logoColor=white)
![Google Drive](https://img.shields.io/badge/Google_Drive-API-4285F4?style=for-the-badge&logo=googledrive&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-27AE60?style=for-the-badge)

**A Python-based multi-cloud hybrid backup system that ensures agriculture data is always safe — using Local Storage, Google Drive, and AWS S3 with automatic failover.**

*Project ID: PRJN26-055 · BCA (AI, Cloud Computing & DevOps) · Yenepoya Institute · 2023–2026*

</div>

---

## 📌 Table of Contents

- [About the Project](#-about-the-project)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Usage](#-usage)
  - [Run via Terminal](#run-via-terminal)
  - [Run via Streamlit Dashboard](#run-via-streamlit-dashboard)
- [Sample Agriculture Data](#-sample-agriculture-data)
- [Backup Output](#-backup-output)
- [Results](#-results)
- [Project Details](#-project-details)
- [Future Enhancements](#-future-enhancements)
- [Author](#-author)

---

## 📖 About the Project

Agriculture data — crop reports, soil analysis, weather logs, irrigation schedules, and pesticide records — is mission-critical. Losing it due to hardware failure or a single cloud service outage can impact entire farming seasons.

This project simulates a **Multi-Source Backup Strategy** for agriculture documents by backing up a local directory to three different destinations:

1. **Local Folder** — Fast, immediate, timestamped backup
2. **Google Drive** — Cloud backup via Desktop sync
3. **AWS S3** — Scalable object storage backup via `boto3`

If one backup destination fails, the system automatically tries the next — demonstrating the core concepts of **Redundancy** and **Failover** through simple Python file operations.

---

## ✨ Features

- ✅ **Three-tier backup** — Local → Google Drive → AWS S3
- ✅ **Automatic failover** — If one fails, the next is tried automatically
- ✅ **Timestamped backups** — Each run creates a unique `backup_YYYYMMDD_HHMMSS/` folder
- ✅ **Detailed logging** — All operations logged to `backup_log.txt` with level, timestamp, and file info
- ✅ **JSON summary** — `last_backup_summary.json` stores pass/fail result for each method
- ✅ **Streamlit dashboard** — One-click web UI for triggering backups and viewing logs
- ✅ **Sample data generator** — Creates 5 real agriculture files for testing
- ✅ **Critical alerting** — Logs a CRITICAL alert if all three backup methods fail

---

## 🛠 Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.x** | Core scripting language |
| **shutil / os** | Local file copy and directory operations |
| **logging** | Log all backup events to file and terminal |
| **boto3** | AWS SDK — uploads files to S3 |
| **Google Drive Desktop** | Sync files to Google Drive via local folder |
| **google-auth** | Authenticate with Google Cloud service account |
| **Streamlit** | Interactive web dashboard for backup control |
| **JSON** | Store backup result summary |
| **VS Code** | Development IDE |

---

## 🏗 System Architecture

```
agriculture_data/                  ← Source folder (crop, soil, weather files)
        │
        ▼
┌─────────────────────────┐
│   Failover Controller   │   run_backup_with_failover()
│  ─────────────────────  │
│  Step 1: Local Backup   │ ──► local_backup/backup_YYYYMMDD_HHMMSS/
│  Step 2: Google Drive   │ ──► G:\My Drive\AgriBackup\
│  Step 3: AWS S3         │ ──► s3://agri-backup-umer-2026/agriculture_backup/TIMESTAMP/
└─────────────────────────┘
        │
        ▼
last_backup_summary.json   ← { local: true, google_drive: true, aws_s3: true }
backup_log.txt             ← Full timestamped event log
```

**Failover Logic:**
- Step 1 always runs (local backup)
- If local succeeds → cloud backups also run for redundancy
- If local fails → cloud backups attempted as fallback
- If **ALL** methods fail → `CRITICAL` alert logged

---

## 📁 Project Structure

```
AgriBackup/
│
├── backup.py                    # Core backup logic (local, Drive, S3, failover)
├── app.py                       # Streamlit web dashboard
├── service_account.json         # Google Cloud service account credentials
├── backup_log.txt               # Auto-generated: full event log
├── last_backup_summary.json     # Auto-generated: latest backup result
│
├── agriculture_data/            # Source folder (auto-created by sample generator)
│   ├── crop_report_april2026.txt
│   ├── soil_analysis.txt
│   ├── weather_log.txt
│   ├── irrigation_schedule.txt
│   └── pesticide_usage.txt
│
└── local_backup/                # Auto-created local backup destination
    └── backup_YYYYMMDD_HHMMSS/
        └── (copies of all agriculture files)
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- A Google Cloud account with Drive API enabled
- An AWS account (Free Tier is sufficient)
- Google Drive Desktop app installed (for Drive sync)
- VS Code or any Python IDE

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/your-username/agri-multicloud-backup.git
cd agri-multicloud-backup
```

**2. Install required Python packages**
```bash
pip install boto3 google-auth google-auth-oauthlib google-api-python-client streamlit
```

### Configuration

**3. Set up Google Drive**

- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create a new project (e.g., `agribackup`)
- Enable the **Google Drive API**
- Create a **Service Account**, download the JSON key, and save it as `service_account.json`
- Install [Google Drive Desktop](https://www.google.com/drive/download/) and sign in
- Note your AgriBackup folder ID from the Drive URL

**4. Set up AWS S3**

- Log in to [AWS Console](https://aws.amazon.com/)
- Create an S3 bucket (e.g., `agri-backup-yourname-2026`) in your preferred region
- Create an IAM user with `AmazonS3FullAccess` policy
- Copy the **Access Key ID** and **Secret Access Key**

**5. Edit the CONFIG in `backup.py`**

```python
CONFIG = {
    "source_dir":        "./agriculture_data",
    "local_backup_dir":  "./local_backup",
    "gdrive_folder_id":  "YOUR_GOOGLE_DRIVE_FOLDER_ID",
    "gdrive_credentials": "service_account.json",
    "s3_bucket_name":    "your-s3-bucket-name",
    "aws_access_key":    "YOUR_AWS_ACCESS_KEY_ID",
    "aws_secret_key":    "YOUR_AWS_SECRET_ACCESS_KEY",
    "aws_region":        "ap-south-1",
    "log_file":          "./backup_log.txt",
}
```

> ⚠️ **Security Note:** Never commit `service_account.json` or your AWS keys to a public repository. Add them to `.gitignore`.

---

## 💻 Usage

### Run via Terminal

```bash
python backup.py
```

You will see a menu:

```
🌾 Agriculture Multi-Cloud Backup System
─────────────────────────────────────────
1. Create sample data + Run full backup
2. Run backup only (use existing data)
3. Test local backup only
─────────────────────────────────────────
Enter your choice (1/2/3):
```

| Choice | Action |
|--------|--------|
| `1` | Generates 5 sample agriculture files, then runs all three backup methods |
| `2` | Runs all three backup methods on your existing `agriculture_data/` folder |
| `3` | Tests only the local folder backup |

### Run via Streamlit Dashboard

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501` — you will see:

- **📋 Current Configuration** — expandable panel showing all CONFIG values
- **1️⃣ Create Sample Data + Run Full Backup** — one-click full test
- **2️⃣ Run Backup Only** — backup existing data to all three destinations
- **3️⃣ Test Local Backup Only** — quick local test
- **📄 Show Backup Log** — displays `backup_log.txt` inline
- **📊 Show Last Backup Summary** — displays `last_backup_summary.json` inline

---

## 🌱 Sample Agriculture Data

The `create_sample_agriculture_data()` function generates 5 test files:

| File | Contents |
|------|----------|
| `crop_report_april2026.txt` | Crop: Wheat · Yield: 4.2 tons/hectare · Season: Rabi 2025-26 |
| `soil_analysis.txt` | pH: 6.8 · Nitrogen: High · Phosphorus: Medium · Moisture: 32% |
| `weather_log.txt` | Date: 2026-04-11 · Temp: 28°C · Rainfall: 12mm · Humidity: 74% |
| `irrigation_schedule.txt` | Field A: Mon/Wed/Fri 6AM · Field B: Tue/Thu 5AM |
| `pesticide_usage.txt` | Chemical: Endosulfan · Qty: 2L/acre · Applied: 2026-03-15 |

---

## 📊 Backup Output

**`backup_log.txt` (sample)**
```
2026-04-26 02:06:51 [INFO] ============================================================
2026-04-26 02:06:51 [INFO]   AGRICULTURE MULTI-CLOUD BACKUP STARTED
2026-04-26 02:06:51 [INFO]   Source: ./agriculture_data
2026-04-26 02:06:51 [INFO] ============================================================
2026-04-26 02:06:51 [INFO] [LOCAL] Starting backup to: ./local_backup/backup_20260426_020651
2026-04-26 02:06:51 [INFO] [LOCAL] ✅ Success! 5 file(s) backed up
2026-04-26 02:06:52 [INFO] [GDRIVE]   Copied: crop_report_april2026.txt
2026-04-26 02:06:52 [INFO] [GDRIVE] ✅ 5 file(s) syncing to Google Drive!
2026-04-26 02:06:53 [INFO] [AWS S3]   Uploaded: soil_analysis.txt → s3://agri-backup-umer-2026/...
2026-04-26 02:06:53 [INFO] [AWS S3] ✅ 5 file(s) uploaded to S3.
2026-04-26 02:06:53 [INFO] 🎉 Backup completed with at least one successful method.
```

**`last_backup_summary.json`**
```json
{
    "local": true,
    "google_drive": true,
    "aws_s3": true,
    "timestamp": "2026-04-26T02:06:53.648080"
}
```

---

## ✅ Results

All three backup methods were tested and confirmed successful:

| Method | Status | Details |
|--------|--------|---------|
| 🖥️ Local Backup | ✅ SUCCESS | 5 files → `backup_20260426_020653/` |
| ☁️ Google Drive | ✅ SUCCESS | 5 files synced to `AgriBackup/` folder |
| 🪣 AWS S3 | ✅ SUCCESS | 5 files uploaded to `agri-backup-umer-2026` bucket |

---

## 📋 Project Details

| Field | Value |
|-------|-------|
| **Project ID** | PRJN26-055 |
| **Project Title** | Multi-Cloud Hybrid Strategy for Agriculture |
| **Programme** | BCA (Artificial Intelligence, Cloud Computing & DevOps) With IBM & TCS |
| **College** | Yenepoya Institute of Arts, Science, Commerce and Management |
| **Semester** | VI Semester |
| **Academic Year** | 2023–2026 |
| **Student Name** | Muhammed Umer Sufaidh |
| **Register Number** | 23BCAICD085 |
| **Campus ID** | 27079 |

---

## 🔮 Future Enhancements

- [ ] **Scheduled Auto-Backup** — Cron job / Windows Task Scheduler integration for daily automatic backups
- [ ] **Email Alerts on Failure** — SMTP notifications when all backup methods fail
- [ ] **Azure Blob Storage** — Add Microsoft Azure as a 4th cloud backup destination
- [ ] **File Encryption** — Encrypt agriculture files before upload using the `cryptography` library
- [ ] **Backup Versioning UI** — Browse and restore previous backup snapshots from the dashboard
- [ ] **Mobile Notifications** — Push alerts via Telegram Bot API on backup status

---

## 👨‍💻 Author

**Muhammed Umer Sufaidh**

- 🎓 BCA (AI, Cloud Computing & DevOps) · VI Semester · 2023–2026
- 🏫 Yenepoya Institute of Arts, Science, Commerce and Management
- 🪪 Register Number: 23BCAICD085 · Campus ID: 27079
- 📁 Project ID: PRJN26-055

---

<div align="center">

Made with ❤️ for Agriculture Data Safety

*"Redundancy is not a luxury — it is a necessity."*

</div>
