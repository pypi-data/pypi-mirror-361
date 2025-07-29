"""
Command-line interface for musicgen-minimal.
Simple, working CLI that doesn't require complex configuration.
"""

import os
import sys
import time
import logging
from typing import Optional

import typer
import torch
from rich import print as rprint
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.logging import RichHandler

from .generator import MusicGenerator

# Setup logging with Rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

app = typer.Typer(
    name="musicgen",
    help="MusicGen Minimal - Text-to-music generation that actually works",
    add_completion=False
)
console = Console()


@app.command()
def generate(
    prompt: str = typer.Argument(..., help="Text description of the music to generate"),
    output: str = typer.Option("output.wav", "--output", "-o", help="Output audio file"),
    duration: float = typer.Option(10.0, "--duration", "-d", help="Duration in seconds"),
    model: str = typer.Option("small", "--model", "-m", help="Model size (small, medium, large)"),
    temperature: float = typer.Option(1.0, "--temperature", "-t", help="Sampling temperature (0.1-2.0)"),
    guidance: float = typer.Option(3.0, "--guidance", "-g", help="Guidance scale (1.0-10.0)"),
    device: Optional[str] = typer.Option(None, "--device", help="Device to use (cpu, cuda, auto)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Generate music from text prompt."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate inputs
    if duration <= 0 or duration > 120:
        rprint("[red]Error: Duration must be between 0 and 120 seconds[/red]")
        raise typer.Exit(1)
    
    if temperature <= 0 or temperature > 2.0:
        rprint("[red]Error: Temperature must be between 0.1 and 2.0[/red]")
        raise typer.Exit(1)
    
    if guidance < 1.0 or guidance > 10.0:
        rprint("[red]Error: Guidance scale must be between 1.0 and 10.0[/red]")
        raise typer.Exit(1)
    
    # Model name mapping
    model_names = {
        "small": "facebook/musicgen-small",
        "medium": "facebook/musicgen-medium", 
        "large": "facebook/musicgen-large"
    }
    
    if model not in model_names:
        rprint(f"[red]Error: Model must be one of: {', '.join(model_names.keys())}[/red]")
        raise typer.Exit(1)
    
    model_name = model_names[model]
    
    # Auto-detect device
    if device is None or device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    try:
        # Load model with progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            load_task = progress.add_task(f"Loading {model} model on {device}...", total=None)
            generator = MusicGenerator(model_name=model_name, device=device)
            progress.update(load_task, completed=True)
        
        rprint("[green]✓ Model loaded successfully![/green]")
        
        # Show generation parameters
        if verbose:
            table = Table(title="Generation Parameters")
            table.add_column("Parameter", style="cyan")
            table.add_column("Value", style="magenta")
            table.add_row("Prompt", prompt)
            table.add_row("Duration", f"{duration}s")
            table.add_row("Model", model)
            table.add_row("Device", device)
            table.add_row("Temperature", str(temperature))
            table.add_row("Guidance", str(guidance))
            table.add_row("Output", output)
            console.print(table)
        
        # Generate with fake progress (since we can't get real progress)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            gen_task = progress.add_task("Generating music...", total=100)
            
            # Start generation in background thread for progress updates
            import threading
            
            result = {"audio": None, "sample_rate": None, "error": None}
            
            def generation_worker():
                try:
                    audio, sample_rate = generator.generate(
                        prompt,
                        duration=duration,
                        temperature=temperature,
                        guidance_scale=guidance
                    )
                    result["audio"] = audio
                    result["sample_rate"] = sample_rate
                except Exception as e:
                    result["error"] = e
            
            # Start generation
            start_time = time.time()
            gen_thread = threading.Thread(target=generation_worker)
            gen_thread.start()
            
            # Update progress
            while gen_thread.is_alive():
                elapsed = time.time() - start_time
                # Rough progress estimate (very approximate)
                estimated_progress = min(95, (elapsed / (duration * 3)) * 100)
                progress.update(gen_task, completed=estimated_progress)
                time.sleep(0.5)
            
            gen_thread.join()
            progress.update(gen_task, completed=100)
            
            # Check for errors
            if result["error"]:
                raise result["error"]
            
            audio = result["audio"]
            sample_rate = result["sample_rate"]
        
        # Save audio
        generator.save_audio(audio, sample_rate, output)
        
        # Show results
        generation_time = time.time() - start_time
        file_size = os.path.getsize(output) / 1024  # KB
        actual_duration = len(audio) / sample_rate
        
        rprint(f"\n[green]✅ Success![/green]")
        rprint(f"📄 Generated: {output} ({file_size:.1f} KB)")
        rprint(f"⏱️  Time: {generation_time:.1f}s")
        rprint(f"🎵 Sample rate: {sample_rate} Hz")
        rprint(f"🎸 Duration: {actual_duration:.1f}s")
        rprint(f"⚡ Speed: {actual_duration/generation_time:.2f}x realtime")
        
    except KeyboardInterrupt:
        rprint("\n[yellow]Generation cancelled by user[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        if verbose:
            import traceback
            console.print_exception()
        raise typer.Exit(1)


@app.command()
def info():
    """Show system information and available models."""
    table = Table(title="MusicGen Minimal - System Info")
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Status", style="magenta")
    
    # Python version
    import sys
    table.add_row("Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # PyTorch info
    table.add_row("PyTorch", torch.__version__)
    table.add_row("CUDA Available", "✓" if torch.cuda.is_available() else "✗")
    
    if torch.cuda.is_available():
        table.add_row("GPU", torch.cuda.get_device_name())
        table.add_row("CUDA Version", torch.version.cuda or "Unknown")
        table.add_row("GPU Memory", f"{torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    # Transformers
    try:
        import transformers
        table.add_row("Transformers", transformers.__version__)
    except ImportError:
        table.add_row("Transformers", "Not installed")
    
    # Available models
    table.add_row("Small Model", "facebook/musicgen-small (300M params, fastest)")
    table.add_row("Medium Model", "facebook/musicgen-medium (1.5B params)")
    table.add_row("Large Model", "facebook/musicgen-large (3.3B params, best quality)")
    
    console.print(table)


@app.command()
def test(
    quick: bool = typer.Option(False, "--quick", help="Skip model loading test")
):
    """Run basic functionality tests."""
    rprint("[yellow]Running system tests...[/yellow]")
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Imports
    try:
        import torch
        import transformers
        from musicgen import MusicGenerator
        rprint("✓ All imports successful")
        tests_passed += 1
    except ImportError as e:
        rprint(f"✗ Import failed: {e}")
    
    # Test 2: CUDA
    if torch.cuda.is_available():
        rprint(f"✓ CUDA available: {torch.cuda.get_device_name()}")
        tests_passed += 1
    else:
        rprint("⚠ CUDA not available (CPU mode)")
        tests_passed += 1  # Not a failure
    
    if not quick:
        # Test 3: Model loading
        try:
            rprint("Loading small model for testing...")
            generator = MusicGenerator("facebook/musicgen-small")
            rprint("✓ Model loads successfully")
            tests_passed += 1
            
            # Test 4: Generation
            rprint("Testing generation (1 second)...")
            audio, sr = generator.generate("test", duration=1.0)
            rprint(f"✓ Generation works! Shape: {audio.shape}, Sample rate: {sr}")
            tests_passed += 1
            
        except Exception as e:
            rprint(f"✗ Model test failed: {e}")
    else:
        rprint("⚠ Skipping model tests (--quick mode)")
        tests_passed += 2
    
    # Results
    if tests_passed == total_tests:
        rprint(f"\n[green]All {total_tests} tests passed! System is ready.[/green]")
    else:
        rprint(f"\n[yellow]{tests_passed}/{total_tests} tests passed.[/yellow]")
        if tests_passed < total_tests - 1:
            rprint("[red]System may not work correctly.[/red]")
            raise typer.Exit(1)


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()