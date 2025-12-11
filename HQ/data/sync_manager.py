"""
BANDIT DATA SYNC MANAGER
------------------------
Handles asynchronous synchronization between local SQLite databases and Google BigQuery.

Capabilities:
1. Initialize local SQLite DB for Bandit memory (if needed).
2. Sync Schema: Ensure BigQuery dataset/tables match local structure.
3. Sync Data: Upload local rows to BigQuery (Async/Batch).
"""

import os
import sqlite3
import asyncio
from google.cloud import bigquery
from google.api_core.exceptions import NotFound

# Configuration
GCP_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "project-5f169828-6f8d-450b-923")
DATASET_ID = "bandit_memory_core"
LOCAL_DB_PATH = "bandit_memory.db"

class DataSyncManager:
    def __init__(self, project_id=GCP_PROJECT, dataset_id=DATASET_ID):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.client = bigquery.Client(project=self.project_id)
        
    def init_local_db(self):
        """Creates dummy local DB if not exists."""
        conn = sqlite3.connect(LOCAL_DB_PATH)
        c = conn.cursor()
        # Create a simple table for testing sync
        c.execute('''CREATE TABLE IF NOT EXISTS memory_log
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      timestamp TEXT, 
                      agent_name TEXT, 
                      action TEXT, 
                      outcome TEXT)''')
        conn.commit()
        conn.close()
        print(f"✅ Local DB initialized at {LOCAL_DB_PATH}")

    def _get_bq_schema(self):
        """Defines the BigQuery schema mapping."""
        return [
            bigquery.SchemaField("id", "INTEGER"),
            bigquery.SchemaField("timestamp", "STRING"),
            bigquery.SchemaField("agent_name", "STRING"),
            bigquery.SchemaField("action", "STRING"),
            bigquery.SchemaField("outcome", "STRING"),
        ]

    def sync_schema(self):
        """Ensures the Dataset and Table exist in BigQuery."""
        # 1. Create Dataset
        dataset_ref = f"{self.project_id}.{self.dataset_id}"
        try:
            self.client.get_dataset(dataset_ref)
            print(f"ℹ️ Dataset {dataset_ref} exists.")
        except NotFound:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            self.client.create_dataset(dataset)
            print(f"✅ Created dataset {dataset_ref}")

        # 2. Create Table
        table_ref = f"{dataset_ref}.memory_log"
        try:
            self.client.get_table(table_ref)
            print(f"ℹ️ Table {table_ref} exists.")
        except NotFound:
            table = bigquery.Table(table_ref, schema=self._get_bq_schema())
            self.client.create_table(table)
            print(f"✅ Created table {table_ref}")

    async def upload_data_async(self):
        """Reads local SQLite data and uploads new rows to BigQuery in a job."""
        print("⏳ Starting Async Data Sync to BigQuery...")
        
        # Read from SQLite
        conn = sqlite3.connect(LOCAL_DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM memory_log")
        rows = c.fetchall()
        conn.close()

        if not rows:
            print("ℹ️ No data to sync.")
            return

        # Prepare for BQ formatted rows (list of dicts or tuples)
        # Assuming simple mapping for demo
        bq_rows = []
        for r in rows:
            bq_rows.append({
                "id": r[0],
                "timestamp": r[1],
                "agent_name": r[2],
                "action": r[3],
                "outcome": r[4]
            })

        # Insert Rows (Streaming API is easiest for real-time, LoadJob for bulk)
        # We use insert_rows_json for simplicity/speed here
        table_ref = f"{self.project_id}.{self.dataset_id}.memory_log"
        errors = self.client.insert_rows_json(table_ref, bq_rows)
        
        if not errors:
            print(f"✅ Synced {len(bq_rows)} rows to BigQuery.")
        else:
            print(f"❌ Errors syncing data: {errors}")

if __name__ == "__main__":
    # Test Run
    sync = DataSyncManager()
    sync.init_local_db()
    sync.sync_schema()
    
    # Insert Dummy Data locally
    import datetime
    conn = sqlite3.connect(LOCAL_DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO memory_log (timestamp, agent_name, action, outcome) VALUES (?, ?, ?, ?)",
              (str(datetime.datetime.now()), "Bandit", "TestSync", "Success"))
    conn.commit()
    conn.close()
    
    # Run Async Sync
    asyncio.run(sync.upload_data_async())
