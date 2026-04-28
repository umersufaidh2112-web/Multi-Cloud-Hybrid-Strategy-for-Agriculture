"""
========================================================
  Multi-Cloud Hybrid Backup Strategy for Agriculture
  PRJN26-055 | BCA/BSc Project
========================================================
  Backs up agriculture files to:
    1. Local Backup Folder
    2. Google Drive (via API)
    3. AWS S3 (via boto3)

  Failover Logic:
    - Try Local first → if fails, try Google Drive → if fails, try AWS S3
    - All results are logged to backup_log.txt
========================================================
"""

import os
import shutil
import logging
import datetime
import json
from pathlib import Path

# ─────────────────────────────────────────────
# CONFIGURATION — Edit these before running
# ─────────────────────────────────────────────

CONFIG = {
    # Folder containing your agriculture files (crop reports, soil data, etc.)
    "source_dir": "./agriculture_data",

    # Local backup destination folder
    "local_backup_dir": "./local_backup",

    # Google Drive folder ID (get from Drive URL after /folders/)
    "gdrive_folder_id": "13FzUzFp5199i9OIx3E89rFF_Ly5Lu8Nf",

    # Path to your Google service account JSON key file
    "gdrive_credentials": r"C:\Users\shuha\Desktop\AgriBackup\service_account.json",

    # AWS S3 Bucket name
    "s3_bucket_name": "agri-backup-umer-2026",
    # AWS credentials (or use ~/.aws/credentials file)
    "aws_access_key": "AKIA3ALVEI3I75LFSYLZ",
    "aws_secret_key": "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",
    "aws_region":  "ap-south-1",

    # Log file path
    "log_file": "./backup_log.txt",
}

# ─────────────────────────────────────────────
# LOGGING SETUP
# ─────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(CONFIG["log_file"], encoding="utf-8"),
        logging.StreamHandler()  # Also print to terminal
    ]
)
log = logging.getLogger(__name__)


# ═══════════════════════════════════════════════
# 1. LOCAL BACKUP
# ═══════════════════════════════════════════════

def backup_local(source_dir: str, backup_dir: str) -> bool:
    """
    Copy all files from source_dir to a timestamped local backup folder.
    Returns True if successful, False if failed.
    """
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = os.path.join(backup_dir, f"backup_{timestamp}")

        log.info(f"[LOCAL] Starting backup to: {dest}")

        if not os.path.exists(source_dir):
            raise FileNotFoundError(f"Source folder not found: {source_dir}")

        # Copy entire directory
        shutil.copytree(source_dir, dest)

        file_count = sum(len(files) for _, _, files in os.walk(dest))
        log.info(f"[LOCAL] ✅ Success! {file_count} file(s) backed up to {dest}")
        return True

    except Exception as e:
        log.error(f"[LOCAL] ❌ Failed: {e}")
        return False


# ═══════════════════════════════════════════════
# 2. GOOGLE DRIVE BACKUP
# ═══════════════════════════════════════════════

def backup_google_drive(source_dir: str, folder_id: str, credentials_path: str) -> bool:
    """
    Copy files to local Google Drive Desktop sync folder.
    Google Drive Desktop app auto-syncs files to cloud.
    """
    try:
        gdrive_sync_dir = r"G:\My Drive\AgriBackup"
        os.makedirs(gdrive_sync_dir, exist_ok=True)
        log.info(f"[GDRIVE] Copying files to Google Drive folder...")
        uploaded = 0
        for root, dirs, files in os.walk(source_dir):
            for filename in files:
                filepath = os.path.join(root, filename)
                dest_path = os.path.join(gdrive_sync_dir, filename)
                shutil.copy2(filepath, dest_path)
                uploaded += 1
                log.info(f"[GDRIVE]   Copied: {filename}")
        log.info(f"[GDRIVE] Success! {uploaded} file(s) syncing to Google Drive!")
        return True
    except Exception as e:
        log.error(f"[GDRIVE] Failed: {e}")
        return False


# ═══════════════════════════════════════════════
# 3. AWS S3 BACKUP
# ═══════════════════════════════════════════════

def backup_aws_s3(source_dir: str, bucket_name: str,
                  aws_access_key: str, aws_secret_key: str, region: str) -> bool:
    """
    Upload all files from source_dir to an AWS S3 bucket.
    Each file is stored under a timestamped folder in S3.
    Returns True if successful, False if failed.

    Requirements:
        pip install boto3
    """
    try:
        import boto3
        from botocore.exceptions import NoCredentialsError, ClientError

        log.info(f"[AWS S3] Starting S3 backup to bucket: {bucket_name}")

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create S3 client
        s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )

        uploaded = 0
        failed_files = []

        for root, dirs, files in os.walk(source_dir):
            for filename in files:
                filepath = os.path.join(root, filename)
                # Create S3 key with timestamp prefix
                s3_key = f"agriculture_backup/{timestamp}/{filename}"
                try:
                    s3.upload_file(filepath, bucket_name, s3_key)
                    uploaded += 1
                    log.info(f"[AWS S3]   Uploaded: {filename} → s3://{bucket_name}/{s3_key}")

                except (NoCredentialsError, ClientError) as file_err:
                    log.warning(f"[AWS S3]   Could not upload {filename}: {file_err}")
                    failed_files.append(filename)

        if failed_files:
            log.warning(f"[AWS S3] ⚠️  {len(failed_files)} file(s) failed.")

        log.info(f"[AWS S3] ✅ Success! {uploaded} file(s) uploaded to S3.")
        return True

    except ImportError:
        log.error("[AWS S3] ❌ Missing library. Run: pip install boto3")
        return False
    except Exception as e:
        log.error(f"[AWS S3] ❌ Failed: {e}")
        return False


# ═══════════════════════════════════════════════
# 4. FAILOVER CONTROLLER (Main Logic)
# ═══════════════════════════════════════════════

def run_backup_with_failover(config: dict):
    """
    Main failover logic:
      Step 1 → Try Local Backup
      Step 2 → Try Google Drive (if local fails)
      Step 3 → Try AWS S3 (if Drive also fails)
      If ALL fail → alert user
    """
    log.info("=" * 60)
    log.info("  AGRICULTURE MULTI-CLOUD BACKUP STARTED")
    log.info(f"  Source: {config['source_dir']}")
    log.info("=" * 60)

    results = {
        "local": False,
        "google_drive": False,
        "aws_s3": False,
        "timestamp": datetime.datetime.now().isoformat()
    }

    # ── STEP 1: Local Backup ──
    log.info("\n📁 STEP 1: Attempting LOCAL backup...")
    results["local"] = backup_local(config["source_dir"], config["local_backup_dir"])

    if results["local"]:
        log.info("✅ Local backup completed. Cloud backups will also run for redundancy.\n")
    else:
        log.warning("⚠️  Local backup FAILED. Trying cloud options...\n")

    # ── STEP 2: Google Drive ──
    log.info("☁️  STEP 2: Attempting GOOGLE DRIVE backup...")
    results["google_drive"] = backup_google_drive(
        config["source_dir"],
        config["gdrive_folder_id"],
        config["gdrive_credentials"]
    )

    if not results["google_drive"]:
        log.warning("⚠️  Google Drive FAILED. Trying AWS S3...\n")

    # ── STEP 3: AWS S3 ──
    log.info("🪣  STEP 3: Attempting AWS S3 backup...")
    results["aws_s3"] = backup_aws_s3(
        config["source_dir"],
        config["s3_bucket_name"],
        config["aws_access_key"],
        config["aws_secret_key"],
        config["aws_region"]
    )

    # ── FINAL SUMMARY ──
    log.info("\n" + "=" * 60)
    log.info("  BACKUP SUMMARY")
    log.info("=" * 60)
    log.info(f"  Local Backup   : {'✅ SUCCESS' if results['local'] else '❌ FAILED'}")
    log.info(f"  Google Drive   : {'✅ SUCCESS' if results['google_drive'] else '❌ FAILED'}")
    log.info(f"  AWS S3         : {'✅ SUCCESS' if results['aws_s3'] else '❌ FAILED'}")
    log.info("=" * 60)

    # Alert if ALL failed
    if not any([results["local"], results["google_drive"], results["aws_s3"]]):
        log.critical("🚨 ALL BACKUP METHODS FAILED! Data is at risk. Check connections and credentials.")
    else:
        log.info("🎉 Backup completed with at least one successful method.")

    # Save summary to JSON
    summary_path = "./last_backup_summary.json"
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=4)
    log.info(f"\n📋 Summary saved to: {summary_path}")


# ═══════════════════════════════════════════════
# 5. SAMPLE DATA GENERATOR (for testing)
# ═══════════════════════════════════════════════

def create_sample_agriculture_data():
    """Creates dummy agriculture files for testing the backup."""
    data_dir = CONFIG["source_dir"]
    os.makedirs(data_dir, exist_ok=True)

    samples = {
        "crop_report_april2026.txt": "Crop: Wheat\nYield: 4.2 tons/hectare\nSeason: Rabi 2025-26\nStatus: Good",
        "soil_analysis.txt": "pH Level: 6.8\nNitrogen: High\nPhosphorus: Medium\nMoisture: 32%",
        "weather_log.txt": "Date: 2026-04-11\nTemp: 28°C\nRainfall: 12mm\nHumidity: 74%",
        "irrigation_schedule.txt": "Field A: Mon, Wed, Fri - 6AM\nField B: Tue, Thu - 5AM\nField C: Daily - 7AM",
        "pesticide_usage.txt": "Chemical: Endosulfan\nQuantity: 2L/acre\nApplied: 2026-03-15\nNext Due: 2026-04-15"
    }

    for filename, content in samples.items():
        filepath = os.path.join(data_dir, filename)
        with open(filepath, "w") as f:
            f.write(content)

    print(f"✅ Sample agriculture data created in '{data_dir}/' folder")
    print(f"   Files: {list(samples.keys())}\n")


# ═══════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    print("\n🌾 Agriculture Multi-Cloud Backup System")
    print("─" * 45)
    print("1. Create sample data + Run full backup")
    print("2. Run backup only (use existing data)")
    print("3. Test local backup only")
    print("─" * 45)

    choice = input("Enter your choice (1/2/3): ").strip()

    if choice == "1":
        create_sample_agriculture_data()
        run_backup_with_failover(CONFIG)

    elif choice == "2":
        run_backup_with_failover(CONFIG)

    elif choice == "3":
        print("\n📁 Running local backup test only...")
        os.makedirs(CONFIG["source_dir"], exist_ok=True)
        result = backup_local(CONFIG["source_dir"], CONFIG["local_backup_dir"])
        print(f"\nResult: {'✅ Local backup SUCCESS' if result else '❌ Local backup FAILED'}")

    else:
        print("Invalid choice. Please enter 1, 2, or 3.")
