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
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.table import Table
from rich.logging import RichHandler

from .generator import MusicGenerator, GenerationProgress
from .batch import BatchProcessor, create_sample_csv

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
    format: str = typer.Option("auto", "--format", "-f", help="Output format (wav, mp3, auto)"),
    bitrate: str = typer.Option("192k", "--bitrate", "-b", help="MP3 bitrate (128k, 192k, 320k)"),
    device: Optional[str] = typer.Option(None, "--device", help="Device to use (cpu, cuda, auto)"),
    no_progress: bool = typer.Option(False, "--no-progress", help="Disable progress bar"),
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
    
    # Auto-detect format from filename extension
    if format == "auto":
        if output.lower().endswith('.mp3'):
            format = "mp3"
        elif output.lower().endswith('.wav'):
            format = "wav"
        else:
            format = "wav"  # Default to WAV
    
    # Validate format
    if format not in ["wav", "mp3"]:
        rprint(f"[red]Error: Format must be 'wav' or 'mp3', got '{format}'[/red]")
        raise typer.Exit(1)
    
    # Validate bitrate
    valid_bitrates = ["128k", "192k", "256k", "320k"]
    if format == "mp3" and bitrate not in valid_bitrates:
        rprint(f"[red]Error: Bitrate must be one of: {', '.join(valid_bitrates)}[/red]")
        raise typer.Exit(1)
    
    # Ensure output filename has correct extension
    if format == "wav" and not output.lower().endswith('.wav'):
        if '.' in output:
            output = output.rsplit('.', 1)[0] + '.wav'
        else:
            output = output + '.wav'
    elif format == "mp3" and not output.lower().endswith('.mp3'):
        if '.' in output:
            output = output.rsplit('.', 1)[0] + '.mp3'
        else:
            output = output + '.mp3'
    
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
        
        # Check if running on CPU and warn about performance
        if not torch.cuda.is_available():
            rprint("[yellow]⚠️  Running on CPU: Generation will be ~10x slower than realtime[/yellow]")
            if duration > 30:
                estimated_time = duration * 10
                rprint(f"[yellow]   Estimated generation time: ~{estimated_time//60:.0f}m {estimated_time%60:.0f}s[/yellow]")
        
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
        
        # Generate with or without progress
        start_time = time.time()
        
        if no_progress:
            # Original behavior without progress
            if duration > 30:
                rprint(f"[yellow]⚠️  Extended generation: {duration}s will be generated in segments[/yellow]")
                audio, sample_rate = generator.generate_extended(
                    prompt,
                    duration=duration,
                    temperature=temperature,
                    guidance_scale=guidance
                )
            else:
                audio, sample_rate = generator.generate(
                    prompt,
                    duration=duration,
                    temperature=temperature,
                    guidance_scale=guidance
                )
        else:
            # Enhanced progress tracking
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                gen_task = progress.add_task("Generating music...", total=100)
                
                # Progress callback
                def progress_callback(percent, message):
                    progress.update(gen_task, completed=percent, description=message)
                
                # Extended generation callback adapter
                def extended_progress_callback(current, total, message):
                    percentage = (current / total) * 100 if total > 0 else 0
                    progress_callback(percentage, message)
                
                # Use extended generation for > 30 seconds, regular for <= 30 seconds
                if duration > 30:
                    rprint(f"[yellow]⚠️  Extended generation: {duration}s will be generated in segments[/yellow]")
                    audio, sample_rate = generator.generate_extended(
                        prompt,
                        duration=duration,
                        temperature=temperature,
                        guidance_scale=guidance,
                        progress_callback=extended_progress_callback
                    )
                else:
                    # For short audio, use regular generation with progress
                    audio, sample_rate = generator.generate(
                        prompt,
                        duration=duration,
                        temperature=temperature,
                        guidance_scale=guidance,
                        progress_callback=progress_callback
                    )
                
        generation_time = time.time() - start_time
        
        # Save audio in specified format
        final_output = generator.save_audio_as_format(
            audio, sample_rate, output, format=format, bitrate=bitrate, delete_wav=(format == "mp3")
        )
        
        # Show results
        file_size = os.path.getsize(final_output) / 1024  # KB
        actual_duration = len(audio) / sample_rate
        
        # Determine actual format from output file
        actual_format = "mp3" if final_output.lower().endswith('.mp3') else "wav"
        requested_mp3_got_wav = (format == "mp3" and actual_format == "wav")
        
        # Show appropriate status
        if requested_mp3_got_wav:
            rprint(f"\n[yellow]⚠️  Partial Success[/yellow]")
            rprint(f"[yellow]MP3 conversion failed - saved as WAV instead[/yellow]")
            rprint(f"[yellow]To enable MP3:[/yellow]")
            rprint(f"[yellow]  1. Install pydub: pip install 'musicgen-minimal[audio]'[/yellow]")
            rprint(f"[yellow]  2. Install ffmpeg:[/yellow]")
            rprint(f"[yellow]     macOS: brew install ffmpeg[/yellow]")
            rprint(f"[yellow]     Ubuntu: sudo apt install ffmpeg[/yellow]")
            rprint(f"[yellow]     Windows: https://ffmpeg.org/download.html[/yellow]")
        else:
            rprint(f"\n[green]✅ Success![/green]")
        
        rprint(f"📄 Generated: {final_output} ({file_size:.1f} KB)")
        rprint(f"🎵 Format: {actual_format.upper()}{f' @ {bitrate}' if actual_format == 'mp3' else ''}")
        rprint(f"⏱️  Time: {generation_time:.1f}s")
        rprint(f"🎵 Sample rate: {sample_rate} Hz")
        rprint(f"🎸 Duration: {actual_duration:.1f}s")
        rprint(f"⚡ Speed: {actual_duration/generation_time:.2f}x realtime")
        
        # Show extended generation info
        if duration > 30:
            rprint(f"[dim]ℹ️  Extended generation used segment blending (not context-aware)[/dim]")
        
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
def batch(
    csv_file: str = typer.Argument(..., help="CSV file with batch generation tasks"),
    output_dir: str = typer.Option("batch_output", "--output-dir", "-o", help="Output directory for generated files"),
    workers: int = typer.Option(None, "--workers", "-w", help="Number of parallel workers (default: auto)"),
    model: str = typer.Option("small", "--model", "-m", help="Default model size (small, medium, large)"),
    device: Optional[str] = typer.Option(None, "--device", help="Device to use (cpu, cuda, auto)"),
    results_file: str = typer.Option("batch_results.json", "--results", "-r", help="Results file name"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Process multiple music generation tasks from CSV file."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Auto-detect device
    if device is None or device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Validate workers
    if workers is not None and workers < 1:
        rprint("[red]Error: Workers must be >= 1[/red]")
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
    
    try:
        # Initialize batch processor
        processor = BatchProcessor(
            model_name=model_name,
            output_dir=output_dir,
            max_workers=workers,
            device=device
        )
        
        # Load CSV file
        rprint(f"[cyan]Loading batch tasks from {csv_file}...[/cyan]")
        jobs = processor.load_csv(csv_file)
        
        if not jobs:
            rprint("[red]No valid jobs found in CSV file[/red]")
            raise typer.Exit(1)
        
        rprint(f"[green]✓ Loaded {len(jobs)} jobs[/green]")
        
        # Show batch info
        if verbose:
            table = Table(title="Batch Processing Configuration")
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="magenta")
            table.add_row("CSV File", csv_file)
            table.add_row("Output Directory", output_dir)
            table.add_row("Workers", str(processor.max_workers))
            table.add_row("Device", device)
            table.add_row("Default Model", model)
            table.add_row("Total Jobs", str(len(jobs)))
            console.print(table)
        
        # Process batch with progress
        rprint(f"[yellow]🎵 Starting batch processing with {processor.max_workers} workers...[/yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("Processing batch...", total=len(jobs))
            
            def progress_callback(current, total, message):
                progress.update(task, completed=current, description=message)
            
            start_time = time.time()
            results = processor.process_batch(jobs, progress_callback)
            batch_time = time.time() - start_time
        
        # Save results
        processor.save_results(results, results_file)
        
        # Show summary
        processor.print_summary(results)
        
        # Show performance info
        successful_jobs = sum(1 for r in results if r["success"])
        rprint(f"\n[green]✅ Batch processing complete![/green]")
        rprint(f"📊 Processed {len(jobs)} jobs in {batch_time:.1f}s")
        rprint(f"📁 Output directory: {output_dir}")
        rprint(f"📄 Results file: {output_dir}/{results_file}")
        rprint(f"⚡ Throughput: {successful_jobs/batch_time:.2f} jobs/second")
        
    except KeyboardInterrupt:
        rprint("\n[yellow]Batch processing cancelled by user[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        if verbose:
            import traceback
            console.print_exception()
        raise typer.Exit(1)


@app.command("create-sample-csv")
def create_sample_csv_cmd(
    filename: str = typer.Option("sample_batch.csv", "--output", "-o", help="Output CSV filename")
):
    """Create a sample CSV file for batch processing."""
    try:
        create_sample_csv(filename)
        rprint(f"[green]✓ Sample CSV created: {filename}[/green]")
        rprint("\nTo process this batch:")
        rprint(f"[dim]musicgen batch {filename}[/dim]")
        
    except Exception as e:
        rprint(f"[red]Error creating sample CSV: {e}[/red]")
        raise typer.Exit(1)


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