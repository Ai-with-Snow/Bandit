"""
Bandit Response Time Benchmarking Tests
Target: 15 seconds for simple queries like "hi"
Uses rich.live for real-time progress display
"""
import pytest
import time
import httpx
import asyncio
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.layout import Layout
from datetime import datetime

# Configuration
PROXY_URL = "http://localhost:8000/v1/chat/completions"
TARGET_RESPONSE_TIME = 15.0  # Target: 15 seconds max for simple queries
SIMPLE_QUERIES = [
    "hi",
    "hello",
    "what time is it?",
    "1+1",
    "who are you?",
]

console = Console()


def create_result_table(results: list) -> Table:
    """Create a rich table showing test results."""
    table = Table(title="🎯 Bandit Response Time Results", show_header=True)
    table.add_column("Query", style="cyan", width=30)
    table.add_column("Mode", style="magenta")
    table.add_column("Time (s)", justify="right")
    table.add_column("Status", justify="center")
    table.add_column("Model Used", style="dim")
    
    for r in results:
        time_str = f"{r['time']:.2f}"
        if r['time'] <= TARGET_RESPONSE_TIME:
            status = "✅ PASS"
            time_style = "green"
        elif r['time'] <= TARGET_RESPONSE_TIME * 1.5:
            status = "⚠️ SLOW"
            time_style = "yellow"
        else:
            status = "❌ FAIL"
            time_style = "red"
        
        table.add_row(
            r['query'][:28] + "..." if len(r['query']) > 28 else r['query'],
            r['mode'],
            f"[{time_style}]{time_str}[/{time_style}]",
            status,
            r.get('model', 'N/A')
        )
    
    return table


async def query_bandit(query: str, mode: str = "instant") -> dict:
    """Query Bandit proxy and measure response time."""
    start_time = time.perf_counter()
    
    payload = {
        "model": "bandit-v1.0",
        "messages": [{"role": "user", "content": query}],
        "thinking_mode": mode
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(PROXY_URL, json=payload)
            elapsed = time.perf_counter() - start_time
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "time": elapsed,
                    "query": query,
                    "mode": mode,
                    "model": data.get("model", "unknown"),
                    "response": data["choices"][0]["message"]["content"][:100]
                }
            else:
                return {
                    "success": False,
                    "time": elapsed,
                    "query": query,
                    "mode": mode,
                    "error": response.text[:100]
                }
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            return {
                "success": False,
                "time": elapsed,
                "query": query,
                "mode": mode,
                "error": str(e)
            }


class TestResponseTime:
    """Response time benchmark tests for Bandit."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test."""
        self.results = []
    
    @pytest.mark.asyncio
    async def test_instant_mode_simple_hi(self):
        """Test 'hi' query in instant mode - must be under 15s."""
        result = await query_bandit("hi", "instant")
        
        console.print(f"\n[bold]Query:[/bold] 'hi' | [bold]Mode:[/bold] instant")
        console.print(f"[bold]Time:[/bold] {result['time']:.2f}s | [bold]Target:[/bold] {TARGET_RESPONSE_TIME}s")
        
        assert result["success"], f"Query failed: {result.get('error', 'Unknown error')}"
        assert result["time"] <= TARGET_RESPONSE_TIME, \
            f"Response time {result['time']:.2f}s exceeds target {TARGET_RESPONSE_TIME}s"
    
    @pytest.mark.asyncio
    async def test_instant_mode_batch(self):
        """Test all simple queries in instant mode."""
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Testing instant mode...", total=len(SIMPLE_QUERIES))
            
            for query in SIMPLE_QUERIES:
                result = await query_bandit(query, "instant")
                results.append(result)
                progress.update(task, advance=1, description=f"Tested: {query[:20]}...")
        
        # Display results
        console.print(create_result_table(results))
        
        # Calculate stats
        times = [r["time"] for r in results if r["success"]]
        if times:
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            
            console.print(Panel(
                f"[bold]Avg:[/bold] {avg_time:.2f}s | [bold]Min:[/bold] {min_time:.2f}s | [bold]Max:[/bold] {max_time:.2f}s",
                title="📊 Statistics"
            ))
            
            # Assert all passed
            failed = [r for r in results if not r["success"] or r["time"] > TARGET_RESPONSE_TIME]
            assert len(failed) == 0, f"{len(failed)} queries exceeded target time or failed"
    
    @pytest.mark.asyncio
    async def test_auto_mode_simple_query(self):
        """Test simple query in auto mode (uses Reasoning Engine)."""
        result = await query_bandit("hello", "auto")
        
        console.print(f"\n[bold]Query:[/bold] 'hello' | [bold]Mode:[/bold] auto (Reasoning Engine)")
        console.print(f"[bold]Time:[/bold] {result['time']:.2f}s")
        
        assert result["success"], f"Query failed: {result.get('error', 'Unknown error')}"
        # Auto mode is expected to be slower, just verify it works
    
    @pytest.mark.asyncio  
    async def test_thinking_mode_complex_query(self):
        """Test complex query in thinking mode (uses gemini-3-pro)."""
        result = await query_bandit("Think deeply about: What is consciousness?", "thinking")
        
        console.print(f"\n[bold]Query:[/bold] 'What is consciousness?' | [bold]Mode:[/bold] thinking")
        console.print(f"[bold]Time:[/bold] {result['time']:.2f}s | [bold]Model:[/bold] {result.get('model', 'N/A')}")
        
        assert result["success"], f"Query failed: {result.get('error', 'Unknown error')}"


@pytest.mark.asyncio
async def test_live_benchmark():
    """Interactive benchmark with rich.live display."""
    results = []
    modes = ["instant", "auto"]
    
    layout = Layout()
    
    with Live(create_result_table([]), console=console, refresh_per_second=4) as live:
        for mode in modes:
            for query in SIMPLE_QUERIES[:3]:  # Test first 3 queries
                console.print(f"[dim]Testing: {query} ({mode})...[/dim]")
                result = await query_bandit(query, mode)
                results.append(result)
                live.update(create_result_table(results))
                await asyncio.sleep(0.5)  # Brief pause between queries
    
    # Summary
    instant_times = [r["time"] for r in results if r["mode"] == "instant" and r["success"]]
    auto_times = [r["time"] for r in results if r["mode"] == "auto" and r["success"]]
    
    console.print("\n[bold]Summary:[/bold]")
    if instant_times:
        console.print(f"  Instant mode avg: {sum(instant_times)/len(instant_times):.2f}s")
    if auto_times:
        console.print(f"  Auto mode avg: {sum(auto_times)/len(auto_times):.2f}s")


if __name__ == "__main__":
    # Run quick benchmark
    console.print("[bold blue]🚀 Bandit Response Time Benchmark[/bold blue]\n")
    asyncio.run(test_live_benchmark())
