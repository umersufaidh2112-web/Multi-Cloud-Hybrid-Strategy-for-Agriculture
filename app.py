import streamlit as st
import os
import backup  # imports your existing backup.py

st.set_page_config(page_title="Agri Multi-Cloud Backup", page_icon="🌾", layout="centered")

st.title("🌾 Agriculture Multi-Cloud Backup System")
st.markdown("Backup agriculture files to **Local**, **Google Drive**, and **AWS S3** using your existing `backup.py` logic.")

# Show current config
with st.expander("📋 Current Configuration"):
    st.write("**Source Folder:**", backup.CONFIG["source_dir"])
    st.write("**Local Backup Folder:**", backup.CONFIG["local_backup_dir"])
    st.write("**Google Drive Folder ID:**", backup.CONFIG["gdrive_folder_id"])
    st.write("**Google Credentials File:**", backup.CONFIG["gdrive_credentials"])
    st.write("**S3 Bucket Name:**", backup.CONFIG["s3_bucket_name"])
    st.write("**AWS Region:**", backup.CONFIG["aws_region"])

st.divider()

# Button 1: Create sample data + full backup
if st.button("1️⃣ Create Sample Data + Run Full Backup", use_container_width=True):
    with st.spinner("Creating sample data and running full backup..."):
        try:
            backup.create_sample_agriculture_data()
            backup.run_backup_with_failover(backup.CONFIG)
            st.success("✅ Full backup completed! Check backup_log.txt and last_backup_summary.json")
        except Exception as e:
            st.error(f"❌ Error: {e}")

# Button 2: Run backup only
if st.button("2️⃣ Run Backup Only (Use Existing Data)", use_container_width=True):
    with st.spinner("Running full backup..."):
        try:
            backup.run_backup_with_failover(backup.CONFIG)
            st.success("✅ Backup completed! Check backup_log.txt and last_backup_summary.json")
        except Exception as e:
            st.error(f"❌ Error: {e}")

# Button 3: Test local backup only
if st.button("3️⃣ Test Local Backup Only", use_container_width=True):
    with st.spinner("Running local backup test..."):
        try:
            os.makedirs(backup.CONFIG["source_dir"], exist_ok=True)
            result = backup.backup_local(backup.CONFIG["source_dir"], backup.CONFIG["local_backup_dir"])
            if result:
                st.success("✅ Local backup SUCCESS")
            else:
                st.error("❌ Local backup FAILED")
        except Exception as e:
            st.error(f"❌ Error: {e}")

st.divider()

# Show log file
if st.button("📄 Show Backup Log", use_container_width=True):
    log_file = backup.CONFIG["log_file"]
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            st.text_area("backup_log.txt", f.read(), height=300)
    else:
        st.warning("No log file found yet.")

# Show last summary
if st.button("📊 Show Last Backup Summary", use_container_width=True):
    summary_file = "last_backup_summary.json"
    if os.path.exists(summary_file):
        with open(summary_file, "r", encoding="utf-8") as f:
            st.json(f.read())
    else:
        st.warning("No summary file found yet.")

st.info("💡 Run this app with: streamlit run app.py")