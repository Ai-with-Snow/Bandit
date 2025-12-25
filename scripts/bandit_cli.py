"""CLI for interacting with the deployed Bandit Reasoning Engine.

Uses `rich` for a beautiful terminal interface.
"""

import argparse
import os
import sys
import json
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from typing import Optional, List, Dict

# Bandit timezone - always NY/EST
TIMEZONE = ZoneInfo("America/New_York")

from google.cloud import aiplatform
from google.api_core import retry
from google import genai
from google.genai import types
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.theme import Theme
from rich.align import Align
from rich.live import Live
from rich.table import Table
from rich.box import DOUBLE, ROUNDED, HEAVY
from rich.text import Text
from rich.spinner import Spinner
from rich.columns import Columns

# Define a custom theme for LMSIFY branding (Light Mode)
lmsify_theme = Theme({
    "info": "blue",
    "warning": "dark_orange",
    "error": "bold red",
    "success": "bold green",
    "bandit": "bold magenta",
    "user": "bold blue",
})

console = Console(theme=lmsify_theme)

# Read from environment (Cloud Run sets GOOGLE_CLOUD_PROJECT automatically)
DEFAULT_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", os.getenv("GCP_PROJECT", "metal-cable-478318-g8"))
DEFAULT_LOCATION = "us-central1"
# Base64 image transfer (no GCS permissions needed)
# Updated: DAV1D v3 - Fixed spinner + Flash-Lite greetings (2025-12-10)
DEFAULT_ENGINE_ID = "3723065118905335808"
SEARCH_MODEL = os.getenv("BANDIT_SEARCH_MODEL", "gemini-2.5-flash")
RAG_MODEL = os.getenv("BANDIT_RAG_MODEL", "gemini-3-pro-preview")
RAG_EMBED_MODEL = os.getenv("BANDIT_RAG_EMBED_MODEL", "text-embedding-004")
VERTEX_AI_SEARCH_LOCATION = os.getenv("VERTEX_AI_SEARCH_LOCATION", "global")
VERTEX_AI_SEARCH_DATA_STORE_ID = os.getenv("VERTEX_AI_SEARCH_DATA_STORE_ID")

# Memory configuration
SHORT_TERM_MEMORY_LIMIT = 1000  # Session context: last 1000 messages
MEMORY_FILE = Path("HQ/memory/conversations.json")
SQLITE_DB = Path("HQ/memory/bandit_memory.db")  # Local SQLite for offline access

class MemoryManager:
    """Manages short-term and long-term conversation memory with BigQuery sync.
    
    Features:
    - Short-term: Last 1000 messages in session
    - Primer: Last 48 hours loaded lazily after 60 seconds
    - Long-term: BigQuery + SQLite searchable storage
    """
    
    def __init__(self, project_id: str):
        self.conversation_history: List[Dict] = []
        self.primer_context: str = ""  # 48-hour context summary
        self.project_id = project_id
        self.dataset_id = "bandit_memory"
        self.table_id = "conversations"
        self.bq_client = None
        self.query_count = 0
        self.history_loaded = False
        self.primer_loaded = False
        self.session_start = datetime.now(TIMEZONE)
        self.background_tasks = set()
    
    def _load_local_instant(self):
        """Load from local JSON instantly on startup - no blocking."""
        try:
            if MEMORY_FILE.exists():
                with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load last session's messages
                if data.get('sessions') and len(data['sessions']) > 0:
                    last_session = data['sessions'][-1]
                    self.conversation_history = last_session.get('messages', [])[-SHORT_TERM_MEMORY_LIMIT:]
                    if self.conversation_history:
                        console.print(f"[dim]⚡ Loaded {len(self.conversation_history)} messages from local cache[/dim]")
        except Exception as e:
            console.print(f"[dim]Local load skipped: {e}[/dim]")
    
    def _init_bigquery_background(self):
        """Initialize BigQuery client in background thread."""
        try:
            from google.cloud import bigquery
            self.bq_client = bigquery.Client(project=self.project_id)
            
            # Create dataset if it doesn't exist
            dataset_ref = f"{self.project_id}.{self.dataset_id}"
            try:
                self.bq_client.get_dataset(dataset_ref)
            except Exception:
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = "us-central1"
                self.bq_client.create_dataset(dataset)
            
            # Create table if it doesn't exist
            table_ref = f"{dataset_ref}.{self.table_id}"
            try:
                self.bq_client.get_table(table_ref)
            except Exception:
                schema = [
                    bigquery.SchemaField("session_id", "STRING", mode="REQUIRED"),
                    bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
                    bigquery.SchemaField("role", "STRING", mode="REQUIRED"),
                    bigquery.SchemaField("content", "STRING", mode="REQUIRED"),
                    bigquery.SchemaField("message_index", "INTEGER", mode="REQUIRED"),
                ]
                table = bigquery.Table(table_ref, schema=schema)
                self.bq_client.create_table(table)
                
        except Exception as e:
            self.bq_client = None
    
    def _init_bigquery(self):
        """Initialize BigQuery client and ensure table exists."""
        try:
            from google.cloud import bigquery
            self.bq_client = bigquery.Client(project=self.project_id)
            
            # Create dataset if it doesn't exist
            dataset_ref = f"{self.project_id}.{self.dataset_id}"
            try:
                self.bq_client.get_dataset(dataset_ref)
            except Exception:
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = "us-central1"
                self.bq_client.create_dataset(dataset)
                console.print("[dim]Created BigQuery dataset for memory storage[/dim]")
            
            # Create table if it doesn't exist
            table_ref = f"{dataset_ref}.{self.table_id}"
            try:
                self.bq_client.get_table(table_ref)
            except Exception:
                schema = [
                    bigquery.SchemaField("session_id", "STRING", mode="REQUIRED"),
                    bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
                    bigquery.SchemaField("role", "STRING", mode="REQUIRED"),
                    bigquery.SchemaField("content", "STRING", mode="REQUIRED"),
                    bigquery.SchemaField("message_index", "INTEGER", mode="REQUIRED"),
                ]
                table = bigquery.Table(table_ref, schema=schema)
                self.bq_client.create_table(table)
                console.print("[dim]Created BigQuery table for conversations[/dim]")
                
        except Exception as e:
            console.print(f"[warning]BigQuery init failed: {e}. Using local storage only.[/warning]")
            self.bq_client = None
    
    async def _load_from_bigquery_async(self):
        """Load history from BigQuery in background."""
        if not self.bq_client or self.history_loaded:
            return
            
        try:
            query = f"""
                SELECT role, content, timestamp
                FROM `{self.project_id}.{self.dataset_id}.{self.table_id}`
                WHERE session_id = (
                    SELECT session_id 
                    FROM `{self.project_id}.{self.dataset_id}.{self.table_id}`
                    ORDER BY timestamp DESC 
                    LIMIT 1
                )
                ORDER BY message_index ASC
            """
            
            # Run query in executor to avoid blocking
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, 
                lambda: list(self.bq_client.query(query).result())
            )
            
            loaded_messages = []
            for row in results:
                loaded_messages.append({
                    'role': row.role,
                    'content': row.content,
                    'timestamp': row.timestamp.isoformat()
                })
            
            if loaded_messages:
                # Merge with current history, avoiding duplicates
                self.conversation_history = loaded_messages + self.conversation_history
                # Keep within limit
                if len(self.conversation_history) > SHORT_TERM_MEMORY_LIMIT:
                    self.conversation_history = self.conversation_history[-SHORT_TERM_MEMORY_LIMIT:]
                console.print(f"[dim]Loaded {len(loaded_messages)} messages from BigQuery[/dim]")
            
            self.history_loaded = True
        except Exception as e:
            console.print(f"[warning]Background load failed: {e}[/warning]")
    
    async def _load_48h_primer_async(self):
        """Load last 48 hours of conversations for context priming (sync DOWN)."""
        if not self.bq_client or self.primer_loaded:
            return
            
        try:
            query = f"""
                SELECT role, content, timestamp
                FROM `{self.project_id}.{self.dataset_id}.{self.table_id}`
                WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 48 HOUR)
                ORDER BY timestamp DESC
                LIMIT 500
            """
            
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, 
                lambda: list(self.bq_client.query(query).result())
            )
            
            if results:
                # Build a summary of recent activity for primer context
                topics = set()
                for row in results[:100]:  # Analyze top 100
                    content = row.content[:200] if row.content else ""
                    # Extract key topics (simple approach)
                    for word in content.split():
                        if len(word) > 5:
                            topics.add(word.lower())
                
                self.primer_context = f"Recent topics (48h): {', '.join(list(topics)[:20])}"
                console.print(f"[dim]📚 Primer loaded: {len(results)} messages from last 48h[/dim]")
            
            self.primer_loaded = True
        except Exception as e:
            console.print(f"[dim]Primer load skipped: {e}[/dim]")
    
    async def maybe_load_history(self):
        """Load history lazily - instant local, 60s primer from cloud."""
        self.query_count += 1
        
        # Check if 60 seconds have passed - load 48h primer
        elapsed = (datetime.now(TIMEZONE) - self.session_start).total_seconds()
        if elapsed >= 60 and not self.primer_loaded:
            task = asyncio.create_task(self._load_48h_primer_async())
            self.background_tasks.add(task)
            task.add_done_callback(self.background_tasks.discard)
    
    async def save_to_cloud_async(self):
        """Save to BigQuery in background."""
        if not self.bq_client:
            return
            
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            from google.cloud import bigquery
            
            rows_to_insert = []
            for idx, msg in enumerate(self.conversation_history):
                rows_to_insert.append({
                    "session_id": session_id,
                    "timestamp": datetime.fromisoformat(msg['timestamp']),
                    "role": msg['role'],
                    "content": msg['content'],
                    "message_index": idx
                })
            
            # Run insert in executor to avoid blocking
            loop = asyncio.get_event_loop()
            table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
            
            errors = await loop.run_in_executor(
                None,
                lambda: self.bq_client.insert_rows_json(table_ref, rows_to_insert)
            )
            
            if not errors:
                console.print(f"[dim]Synced {len(rows_to_insert)} messages to BigQuery[/dim]")
            else:
                console.print(f"[warning]BigQuery sync errors: {errors}[/warning]")
                
        except Exception as e:
            console.print(f"[warning]Cloud sync failed: {e}[/warning]")
    
    async def save_long_term_memory(self):
        """Save conversation to persistent storage (local + cloud async)."""
        # Save to local file (fast, synchronous)
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = {'sessions': []}
            if MEMORY_FILE.exists():
                with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            session = {
                'timestamp': datetime.now().isoformat(),
                'messages': self.conversation_history
            }
            data['sessions'].append(session)
            data['sessions'] = data['sessions'][-10:]
            
            with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            console.print(f"[warning]Could not save locally: {e}[/warning]")
        
        # Trigger background cloud save
        task = asyncio.create_task(self.save_to_cloud_async())
        self.background_tasks.add(task)
        task.add_done_callback(self.background_tasks.discard)
    
    async def wait_for_background_tasks(self):
        """Wait for all background tasks to complete."""
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
    
    def add_message(self, role: str, content: str):
        """Add a message to conversation history."""
        self.conversation_history.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        
        if len(self.conversation_history) > SHORT_TERM_MEMORY_LIMIT:
            self.conversation_history = self.conversation_history[-SHORT_TERM_MEMORY_LIMIT:]
    
    def get_context(self) -> str:
        """Get conversation context for the model, including 48h primer."""
        parts = []
        
        # Include primer context if loaded
        if self.primer_context:
            parts.append(f"[PRIMER] {self.primer_context}")
        
        # Include recent conversation
        if self.conversation_history:
            parts.append("Previous conversation:")
            for msg in self.conversation_history[-20:]:
                role = msg['role'].upper()
                content = msg['content']
                parts.append(f"{role}: {content}")
        
        return "\n".join(parts) if parts else ""

def get_engine_resource_name(project: str, location: str, engine_id: str) -> str:
    """Constructs the full resource name for the Reasoning Engine."""
    return f"projects/{project}/locations/{location}/reasoningEngines/{engine_id}"

def _resolve_model_location(model_name: str, requested_location: str) -> str:
    """Route models that require global endpoints; otherwise use requested/default."""
    if model_name.startswith("gemini-3-") or model_name.startswith("text-embedding-"):
        return "global"
    return requested_location or DEFAULT_LOCATION

def _load_credentials():
    """Load ADC credentials, supporting JSON in env for fileless auth."""
    from google.auth.transport.requests import Request
    from google.auth import default
    from google.oauth2 import service_account
    
    json_blob = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    
    if json_blob:
        try:
            info = json.loads(json_blob)
            creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
            creds.refresh(Request())
            return creds
        except Exception as exc:
            console.print(f"[warning]Failed to load GOOGLE_APPLICATION_CREDENTIALS_JSON: {exc}. Falling back to ADC.[/warning]")
    
    creds, _ = default(scopes=scopes)
    creds.refresh(Request())
    return creds


def query_engine(client, resource_name: str, prompt: str, context: str = "", location: str = DEFAULT_LOCATION) -> str:
    """Queries the Reasoning Engine via the AI Platform API."""
    import requests
    
    # Get credentials
    credentials = _load_credentials()
    
    # Construct the API endpoint
    resolved_location = location or DEFAULT_LOCATION
    api_endpoint = f"https://{resolved_location}-aiplatform.googleapis.com/v1beta1/{resource_name}:query"
    
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json"
    }
    
    # Add context to prompt if available
    full_prompt = f"{context}\n\nCurrent query: {prompt}" if context else prompt
    
    # Reasoning Engine REST API requires both 'input' and 'classMethod'
    payload = {
        "input": {"prompt": full_prompt},
        "classMethod": "query"
    }
    
    response = requests.post(api_endpoint, headers=headers, json=payload)
    
    # Enhanced error handling
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        error_detail = ""
        try:
            error_detail = f"\nAPI Response: {response.text}"
        except:
            pass
        raise Exception(f"{str(e)}{error_detail}")
    
    result = response.json()
    output_text = result.get("output", str(result))
    
    # Process potential image data (Base64)
    import re
    import base64
    import os
    from datetime import datetime
    
    # Check for [IMAGE_B64] tag
    img_pattern = r'\[IMAGE_B64\](.*?)\[/IMAGE_B64\]'
    match = re.search(img_pattern, output_text, re.DOTALL)
    
    if match:
        try:
            b64_data = match.group(1).strip()
            
            # Create directory if needed
            os.makedirs("generated_images", exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_images/bandit_img_{timestamp}.png"
            
            # Decode and save
            with open(filename, "wb") as f:
                f.write(base64.b64decode(b64_data))
            
            # Replace base64 block with success message
            output_text = output_text.replace(match.group(0), f"\n🖼️  Image saved: {os.path.abspath(filename)}\n")
            
        except Exception as e:
            output_text = output_text.replace(match.group(0), f"\n❌ Image save error: {str(e)}\n")

    return output_text

def run_vertex_search(query: str, project: str, location: str) -> str:
    """Execute a Vertex-grounded search via google-genai tools."""
    resolved_location = _resolve_model_location(SEARCH_MODEL, location)
    search_client = genai.Client(vertexai=True, project=project, location=resolved_location)
    tools = [types.Tool(google_search=types.GoogleSearchRetrieval())]

    response = search_client.models.generate_content(
        model=SEARCH_MODEL,
        contents=query,
        tools=tools,
    )
    return response.text or "No results returned."


def stream_query_engine(client, resource_name: str, prompt: str, context: str = "", location: str = DEFAULT_LOCATION) -> str:
    """Queries the Reasoning Engine with status spinner display.
    
    Shows a thinking animation while waiting for the response.
    """
    import requests
    import time
    
    # Get credentials
    credentials = _load_credentials()
    
    # Construct the API endpoint
    resolved_location = location or DEFAULT_LOCATION
    api_endpoint = f"https://{resolved_location}-aiplatform.googleapis.com/v1beta1/{resource_name}:query"
    
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json"
    }
    
    # Add context to prompt if available
    full_prompt = f"{context}\n\nCurrent query: {prompt}" if context else prompt
    
    payload = {
        "input": {"prompt": full_prompt},
        "classMethod": "query"
    }
    
    start_time = time.time()
    
    # Simple spinner status (works reliably on Windows)
    with console.status("[bold magenta]🧠 Thinking...[/bold magenta]", spinner="dots") as status:
        try:
            response = requests.post(api_endpoint, headers=headers, json=payload, timeout=120)
            elapsed = time.time() - start_time
            status.update(f"[bold magenta]📥 Processing... ({elapsed:.1f}s)[/bold magenta]")
            
            response.raise_for_status()
            result = response.json()
            output_text = result.get("output", str(result))
            
        except requests.exceptions.HTTPError as e:
            elapsed = time.time() - start_time
            error_detail = ""
            try:
                error_detail = f"\nAPI Response: {response.text}"
            except Exception:
                pass
            raise Exception(f"{str(e)}{error_detail}")
        except Exception as e:
            raise
    
    # Show completion time
    elapsed = time.time() - start_time
    console.print(f"[dim]✓ Response in {elapsed:.1f}s[/dim]")
    
    # Process potential image data (Base64)
    import re
    import base64
    
    img_pattern = r'\[IMAGE_B64\](.*?)\[/IMAGE_B64\]'
    match = re.search(img_pattern, output_text, re.DOTALL)
    
    if match:
        try:
            b64_data = match.group(1).strip()
            os.makedirs("generated_images", exist_ok=True)
            timestamp = datetime.now(TIMEZONE).strftime("%Y%m%d_%H%M%S")
            filename = f"generated_images/bandit_img_{timestamp}.png"
            
            with open(filename, "wb") as f:
                f.write(base64.b64decode(b64_data))
            
            output_text = output_text.replace(match.group(0), f"\n🖼️  Image saved: {os.path.abspath(filename)}\n")
        except Exception as e:
            output_text = output_text.replace(match.group(0), f"\n❌ Image save error: {str(e)}\n")
    
    return output_text

def run_rag(query: str, project: str, data_store_location: str, data_store_id: str) -> str:
    """Grounds responses on a Vertex AI Search data store."""
    from google.cloud import discoveryengine_v1 as discoveryengine

    client = discoveryengine.SearchServiceClient()

    serving_config = client.serving_config_path(
        project=project,
        location=data_store_location,
        data_store=data_store_id,
        serving_config="default_config",
    )

    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=5,
        query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
            condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
        ),
        spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
            mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
        ),
    )

    response = client.search(request)
    
    # Defensive null checks for document content
    snippets = []
    for r in response.results:
        if hasattr(r, 'document') and r.document and hasattr(r.document, 'content') and r.document.content:
            snippets.append(r.document.content)

    if not snippets:
        return "No relevant documents found in Vertex AI Search."

    context = "\n\n".join(snippets)

    rag_client = genai.Client(vertexai=True, project=project, location=_resolve_model_location(RAG_MODEL, "us-central1")) 

    prompt = (
        "Use the following snippets from the knowledge base to answer the question.\n"
        "Cite sources if available in the snippets.\n\n"
        f"Snippets:\n{context}\n\n"
        f"Question: {query}"
    )

    response = rag_client.models.generate_content(
        model=RAG_MODEL,
        contents=prompt,
    )

    return response.text or "No answer produced."

async def main():
    parser = argparse.ArgumentParser(description="Bandit HQ CLI")
    parser.add_argument("--project", default=DEFAULT_PROJECT)
    parser.add_argument("--location", default=DEFAULT_LOCATION)
    parser.add_argument("--engine-id", default=DEFAULT_ENGINE_ID)
    args = parser.parse_args()

    # ASCII Art Banner
    ascii_banner = """
 ███████████                           █████  ███   █████   
░░███░░░░░███                         ░░███  ░░░   ░░███    
 ░███    ░███  ██████   ████████    ███████  ████  ███████  
 ░██████████  ░░░░░███ ░░███░░███  ███░░███ ░░███ ░░░███░   
 ░███░░░░░███  ███████  ░███ ░███ ░███ ░███  ░███   ░███    
 ░███    ░███ ███░░███  ░███ ░███ ░███ ░███  ░███   ░███ ███
 ███████████ ░░████████ ████ █████░░████████ █████  ░░█████ 
░░░░░░░░░░░   ░░░░░░░░ ░░░░ ░░░░░  ░░░░░░░░ ░░░░░    ░░░░░  
"""
    
    # DAV1D-style banner with DOUBLE box
    console.print(Panel(
        Align.center(
            f"[bold magenta]{ascii_banner}[/bold magenta]\n"
            "[bold cyan]HQ Operator[/bold cyan] [dim]×[/dim] [bold green]LMSIFY[/bold green]\n"
            f"[dim]{datetime.now(TIMEZONE).strftime('%B %d, %Y • %I:%M %p EST')}[/dim]"
        ),
        title="[bold green]⚡ BANDIT v1.0[/bold green]",
        border_style="magenta",
        box=DOUBLE,
        expand=True
    ))
    
    # Status table DAV1D-style
    status_table = Table(box=ROUNDED, border_style="cyan", expand=True, show_header=False)
    status_table.add_column("", style="bold cyan", width=20)
    status_table.add_column("", style="white")
    status_table.add_row("🎯 Engine", args.engine_id)
    status_table.add_row("📍 Location", args.location)
    status_table.add_row("🧠 Router", "gemini-2.5-flash-lite")
    status_table.add_row("⚡ Models", "Flash → Pro → Elite (3.0)")
    console.print(status_table)
    console.print()

    try:
        with console.status("[bold green]Initializing Neural Link...[/bold green]", spinner="dots"):
            aiplatform.init(project=args.project, location=args.location)
            from google.cloud.aiplatform_v1 import ReasoningEngineServiceClient
            client = ReasoningEngineServiceClient()
            resource_name = get_engine_resource_name(args.project, args.location, args.engine_id)
        console.print("[success]✓ Link Established[/success]")
    except Exception as e:
        console.print(f"[error]Connection Failed:[/error] {e}")
        import traceback
        console.print(traceback.format_exc())
        return

    console.print("[dim]Type /help for commands, 'exit' to disconnect[/dim]\n")

    # Initialize memory manager - INSTANT local load, background cloud sync
    memory = MemoryManager(args.project)
    memory._load_local_instant()  # Instant local load
    
    # Background BigQuery init (non-blocking)
    import threading
    bq_thread = threading.Thread(target=memory._init_bigquery_background, daemon=True)
    bq_thread.start()

    try:
        while True:
            user_input = Prompt.ask("[bold]You[/bold]")
            
            if user_input.lower() in ["exit", "quit"]:
                console.print("[warning]Saving conversation and terminating link...[/warning]")
                await memory.save_long_term_memory()
                await memory.wait_for_background_tasks()  # Wait for cloud sync
                break
            
            if not user_input.strip():
                continue

            if user_input.lower().startswith("/rag"):
                query = user_input[len("/rag"):].strip()
                if not query:
                    console.print("[warning]Usage: /rag <query>[/warning]")
                    continue

                if not VERTEX_AI_SEARCH_DATA_STORE_ID:
                    console.print("[error]VERTEX_AI_SEARCH_DATA_STORE_ID environment variable not set.[/error]")
                    console.print("[info]Please set this to your Vertex AI Search data store ID to use the /rag command.[/info]")
                    continue

                console.print(Panel(query, title="[bold yellow]RAG[/bold yellow]", border_style="yellow", expand=True))
                try:
                    with console.status("[bandit]Grounding in Vertex AI Search...[/bandit]", spinner="aesthetic"):
                        rag_text = run_rag(query, args.project, VERTEX_AI_SEARCH_LOCATION, VERTEX_AI_SEARCH_DATA_STORE_ID)
                    memory.add_message("user", f"/rag {query}")
                    memory.add_message("bandit", rag_text)
                    console.print(Panel(
                        Markdown(str(rag_text)),
                        title="[bold magenta]Bandit (RAG)[/bold magenta]",
                        border_style="magenta",
                        expand=True
                    ))
                    console.print()
                except Exception as e:
                    console.print(f"[error]RAG search failed:[/error] {e}")
                continue

            if user_input.lower().startswith("/search"):
                query = user_input[len("/search"):].strip()
                if not query:
                    console.print("[warning]Usage: /search <query>[/warning]")
                    continue

                console.print(Panel(query, title="[bold yellow]Search[/bold yellow]", border_style="yellow", expand=True))
                try:
                    with console.status("[bandit]Searching (Vertex)...[/bandit]", spinner="aesthetic"):
                        search_text = run_vertex_search(query, args.project, args.location)
                    memory.add_message("user", f"/search {query}")
                    memory.add_message("bandit", search_text)
                    console.print(Panel(
                        Markdown(str(search_text)),
                        title="[bold magenta]Bandit (Search)[/bold magenta]",
                        border_style="magenta",
                        expand=True
                    ))
                    console.print()
                except Exception as e:
                    console.print(f"[error]Search failed:[/error] {e}")
                continue

            # === DAV1D-INSPIRED COMMANDS ===
            
            # Multi-agent council
            if user_input.lower().startswith("/council"):
                query = user_input[len("/council"):].strip()
                if not query:
                    console.print("[warning]Usage: /council <task or question>[/warning]")
                    continue
                
                try:
                    from scripts.council import run_council
                    memory.add_message("user", f"/council {query}")
                    response = run_council(query, "balanced")
                    memory.add_message("bandit", response)
                except Exception as e:
                    console.print(f"[error]Council failed:[/error] {e}")
                    import traceback
                    console.print(traceback.format_exc())
                continue
            
            # Tree of Thought
            if user_input.lower().startswith("/tot"):
                task = user_input[len("/tot"):].strip()
                if not task:
                    console.print("[warning]Usage: /tot <task to analyze>[/warning]")
                    continue
                
                try:
                    from scripts.prompting import tree_of_thought
                    memory.add_message("user", f"/tot {task}")
                    response = tree_of_thought(task, "deep")
                    memory.add_message("bandit", response)
                except Exception as e:
                    console.print(f"[error]Tree of Thought failed:[/error] {e}")
                continue
            
            # Battle of Bots
            if user_input.lower().startswith("/battle"):
                task = user_input[len("/battle"):].strip()
                if not task:
                    console.print("[warning]Usage: /battle <task for adversarial validation>[/warning]")
                    continue
                
                try:
                    from scripts.prompting import battle_of_bots
                    memory.add_message("user", f"/battle {task}")
                    response = battle_of_bots(task, "deep")
                    memory.add_message("bandit", response)
                except Exception as e:
                    console.print(f"[error]Battle of Bots failed:[/error] {e}")
                continue
            
            # Prompt Optimizer
            if user_input.lower().startswith("/optimize"):
                prompt = user_input[len("/optimize"):].strip()
                if not prompt:
                    console.print("[warning]Usage: /optimize <rough prompt to enhance>[/warning]")
                    continue
                
                try:
                    from scripts.prompting import optimize_prompt
                    memory.add_message("user", f"/optimize {prompt}")
                    response = optimize_prompt(prompt, "balanced")
                    memory.add_message("bandit", response)
                except Exception as e:
                    console.print(f"[error]Prompt optimization failed:[/error] {e}")
                continue
            
            # Shell Execution
            if user_input.lower().startswith("/exec"):
                cmd = user_input[len("/exec"):].strip()
                if not cmd:
                    console.print("[warning]Usage: /exec <command>[/warning]")
                    continue
                
                console.print(Panel(cmd, title="[bold cyan]Execute[/bold cyan]", border_style="cyan", expand=True))
                try:
                    import subprocess
                    import sys as sys_module
                    
                    console.print(f"[cyan][EXEC] {cmd}[/cyan]")
                    console.print(f"[dim]Working directory: {os.getcwd()}[/dim]\n")
                    
                    # Use PowerShell on Windows
                    if sys_module.platform == "win32":
                        full_command = ["powershell", "-Command", cmd]
                    else:
                        full_command = ["bash", "-c", cmd]
                    
                    result = subprocess.run(
                        full_command,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.stdout:
                        console.print(f"[green]{result.stdout}[/green]")
                    if result.stderr:
                        console.print(f"[red]{result.stderr}[/red]")
                    
                    success = result.returncode == 0
                    console.print(f"[{'green' if success else 'red'}][{'✓' if success else '✗'}] Exit code: {result.returncode}[/]")
                    
                    memory.add_message("user", f"/exec {cmd}")
                    memory.add_message("bandit", result.stdout or result.stderr or f"Exit code: {result.returncode}")
                except subprocess.TimeoutExpired:
                    console.print(f"[red]Command timed out after 30 seconds[/red]")
                except Exception as e:
                    console.print(f"[error]Execution failed:[/error] {e}")
                continue
            
            # Help command (updated)
            if user_input.lower() in ["/help", "/h", "/?", "/commands"]:
                console.print(Panel(
                    Markdown("""## Bandit HQ Commands

### Search & RAG
- `/search <query>` - Google Search grounding
- `/rag <query>` - Search HQ knowledge base

### Multi-Agent Council
- `/council <task>` - Convene Bandit, Ice Wire, and Cipher

### Advanced Prompting
- `/tot <task>` - Tree of Thought (multi-path analysis)
- `/battle <task>` - Battle of Bots (adversarial validation)
- `/optimize <prompt>` - Enhance a rough prompt

### System
- `/exec <command>` - Execute shell command
- `/help` - Show this help

### Session
- `exit` or `quit` - Save and disconnect
"""),
                    title="[bold gold]Bandit HQ Commands[/bold gold]",
                    border_style="gold",
                    expand=True
                ))
                continue

            # Trigger lazy history load after 2nd query
            await memory.maybe_load_history()

            # Display user message in gold panel
            console.print(Panel(
                user_input,
                title="[bold yellow]You[/bold yellow]",
                border_style="yellow",
                expand=True
            ))
            console.print()

            # Add to memory
            memory.add_message("user", user_input)

            try:
                # Use streaming query with rich.Live display
                context = memory.get_context()
                response = stream_query_engine(
                    client,
                    resource_name,
                    user_input,
                    context,
                    location=args.location,
                )
                
                # Add response to memory
                memory.add_message("bandit", response)
                
                # Display Bandit response in magenta panel with DOUBLE border
                console.print(Panel(
                    Markdown(str(response)),
                    title=f"[bold magenta]Bandit[/bold magenta] [dim]{datetime.now(TIMEZONE).strftime('%I:%M %p EST')}[/dim]",
                    border_style="magenta",
                    box=DOUBLE,
                    expand=True
                ))
                console.print()
                
            except Exception as e:
                console.print(f"[error]Transmission Error:[/error] {e}")
                import traceback
                console.print(traceback.format_exc())
    
    except KeyboardInterrupt:
        console.print("\n[warning]Saving conversation...[/warning]")
        await memory.save_long_term_memory()
        await memory.wait_for_background_tasks()

if __name__ == "__main__":
    asyncio.run(main())
