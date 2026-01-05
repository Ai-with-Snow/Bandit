"""
Performance test - 100 iterations with timing stats
Goal: Make each iteration faster
"""
import time
import httpx
import statistics
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

PROXY_URL = "http://localhost:8000/v1/chat/completions"
console = Console()

def run_single_test(query: str = "hi") -> float:
    """Run a single query and return response time."""
    start = time.perf_counter()
    try:
        r = httpx.post(PROXY_URL, json={
            "model": "test",
            "messages": [{"role": "user", "content": query}],
            "thinking_mode": "instant"
        }, timeout=60)
        if r.status_code != 200:
            return -1
        return time.perf_counter() - start
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return -1

def run_performance_test(num_iterations: int = 100):
    """Run performance test with stats."""
    console.print(f"\n[bold blue]🚀 Performance Test - {num_iterations} iterations[/bold blue]\n")
    
    times = []
    errors = 0
    best_time = float('inf')
    worst_time = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Testing...", total=num_iterations)
        
        for i in range(num_iterations):
            elapsed = run_single_test("hi")
            
            if elapsed > 0:
                times.append(elapsed)
                if elapsed < best_time:
                    best_time = elapsed
                if elapsed > worst_time:
                    worst_time = elapsed
                
                # Update progress description
                avg = statistics.mean(times) if times else 0
                progress.update(task, advance=1, 
                    description=f"Iter {i+1}: {elapsed:.2f}s | Avg: {avg:.2f}s | Best: {best_time:.2f}s")
            else:
                errors += 1
                progress.update(task, advance=1, description=f"Iter {i+1}: ERROR")
    
    # Final stats
    if times:
        console.print("\n[bold green]📊 Final Results[/bold green]")
        table = Table(show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")
        
        table.add_row("Total Iterations", str(num_iterations))
        table.add_row("Successful", str(len(times)))
        table.add_row("Errors", str(errors))
        table.add_row("Best Time", f"{best_time:.3f}s")
        table.add_row("Worst Time", f"{worst_time:.3f}s")
        table.add_row("Average", f"{statistics.mean(times):.3f}s")
        table.add_row("Median", f"{statistics.median(times):.3f}s")
        if len(times) > 1:
            table.add_row("Std Dev", f"{statistics.stdev(times):.3f}s")
        table.add_row("P95", f"{sorted(times)[int(len(times)*0.95)]:.3f}s" if len(times) >= 20 else "N/A")
        
        console.print(table)
        
        # Target check
        target = 15.0
        under_target = sum(1 for t in times if t <= target)
        console.print(f"\n[bold]Under {target}s target: {under_target}/{len(times)} ({100*under_target/len(times):.1f}%)[/bold]")
        
        return statistics.mean(times)
    else:
        console.print("[red]All tests failed![/red]")
        return -1

if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10  # Default 10, pass arg for more
    run_performance_test(n)
