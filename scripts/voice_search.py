import os
import requests
from datetime import datetime, timedelta
from pytz import timezone
import json
import asyncio

# --- LAZY LOADER ---
class LazyLoader:
    def __getattr__(self, name):
        if name == "bigquery": from google.cloud import bigquery; return bigquery
        if name == "storage": from google.cloud import storage; return storage
        if name == "firestore": from google.cloud import firestore; return firestore
        if name == "speech": from google.cloud import speech; return speech
        if name == "texttospeech": from google.cloud import texttospeech; return texttospeech
        if name == "documentai": from google.cloud import documentai_v1 as documentai; return documentai
        if name == "aiplatform": from google.cloud import aiplatform; return aiplatform
        if name == "vertexai": import vertexai; return vertexai
        if name == "genai": from google import genai; return genai
        if name == "types": from google.genai import types; return types
        if name == "SentenceTransformer": from sentence_transformers import SentenceTransformer; return SentenceTransformer
        if name == "faiss": import faiss; return faiss
        if name == "np": import numpy as np; return np
        if name == "BeautifulSoup": from bs4 import BeautifulSoup; return BeautifulSoup
        if name == "GenerativeModel": from vertexai.generative_models import GenerativeModel; return GenerativeModel
        if name == "Tool": from vertexai.generative_models import Tool; return Tool
        if name == "grounding": from vertexai.preview.generative_models import grounding; return grounding
        raise AttributeError(f"Module {name} not found")

lib = LazyLoader()

class GCPVoiceAIBackend:
    """Complete GCP-integrated voice AI backend (Lazy Loaded)"""
    
    def __init__(self, project_id=None, location="us-central1", client=None):
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT")
        self.location = location
        self.genai_client = client # Optional reuse
        
        # Lazy clients
        self._bq_client = None
        self._storage_client = None
        self._firestore_client = None
        
        # Init Vertex AI (Lazy)
        if self.project_id:
             try:
                # We don't block on init, assume it works when needed
                pass
             except Exception as e:
                 print(f"[Backend] Vertex AI Init Warning: {e}")

    # --- CLIENT PROPERTIES ---
    @property
    def bq_client(self):
        if not self._bq_client: self._bq_client = lib.bigquery.Client(project=self.project_id)
        return self._bq_client
    
    @property
    def storage_client(self):
        if not self._storage_client: self._storage_client = lib.storage.Client(project=self.project_id)
        return self._storage_client

    # ============ 2026 COUNTDOWN TIME ============
    def get_eastern_time_advanced(self):
        """Get current Eastern time with New Year 2026 countdown."""
        try:
            eastern = timezone('US/Eastern')
            current_time = datetime.now(eastern)
            
            # Calculate countdown to 2026
            new_year_2026 = eastern.localize(datetime(2026, 1, 1, 0, 0, 0))
            time_until_2026 = new_year_2026 - current_time
            
            days_until = time_until_2026.days
            hours_until = time_until_2026.seconds // 3600
            minutes = (time_until_2026.seconds % 3600) // 60
            
            time_str = current_time.strftime('%I:%M %p %Z')
            countdown_msg = f"{days_until} days to 2026"
            
            return f"{time_str} | Countdown: {countdown_msg}"
        except Exception:
             return datetime.now().strftime('%H:%M')

    # ============ WEB FETCH ============
    def web_fetch(self, url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = lib.BeautifulSoup(response.content, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            text = ' '.join(phrase.strip() for line in lines for phrase in line.split("  ") if phrase.strip())
            
            return text[:5000]
        except Exception as e:
            return f"Error fetching {url}: {e}"

    # ============ GROUNDING (VERTEX) ============
    def grounding_search(self, query):
        """Native Vertex AI Search."""
        try:
            lib.vertexai.init(project=self.project_id, location=self.location)
            model = lib.GenerativeModel("gemini-2.0-flash-exp")
            
            tool = lib.Tool.from_google_search_retrieval(
                lib.grounding.GoogleSearchRetrieval()
            )
            
            response = model.generate_content(
                query,
                tools=[tool],
            )
            return response.text
        except Exception as e:
            # Fallback
            try:
                grounding_tool = lib.types.Tool(google_search=lib.types.GoogleSearch())
                response = self.genai_client.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=query,
                    config=lib.types.GenerateContentConfig(tools=[grounding_tool])
                )
                return response.text
            except Exception as e2:
                return f"Grounding Error: {e}"

    # ============ BIGQUERY ============
    def bigquery_query(self, sql):
        try:
            query_job = self.bq_client.query(sql)
            results = query_job.result()
            rows = [dict(row) for row in results]
            return json.dumps(rows[:10], default=str)
        except Exception as e:
            return f"BQ Error: {e}"

    # ============ GCS ============
    def list_gcs(self, bucket_name, prefix=''):
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blobs = bucket.list_blobs(prefix=prefix)
            return json.dumps([b.name for b in blobs][:20])
        except Exception as e:
             return f"GCS Error: {e}"

    def read_gcs(self, bucket_name, filename):
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(filename)
            return blob.download_as_text()[:5000]
        except Exception as e:
            return f"GCS Read Error: {e}"
