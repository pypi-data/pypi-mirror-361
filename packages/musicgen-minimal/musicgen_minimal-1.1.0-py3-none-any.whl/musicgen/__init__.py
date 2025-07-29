"""
MusicGen Minimal - Simple text-to-music generation that actually works.

This package provides a dead-simple interface to Facebook's MusicGen model
without the complexity of enterprise architectures or broken abstractions.

Example usage:
    from musicgen import MusicGenerator, quick_generate
    
    # Full control
    generator = MusicGenerator()
    audio, sample_rate = generator.generate("upbeat jazz piano", duration=10.0)
    generator.save_audio(audio, sample_rate, "output.wav")
    
    # Quick generation
    quick_generate("peaceful ambient music", "peaceful.wav", duration=30)

CLI usage:
    musicgen generate "peaceful ambient music" -d 30 -o peaceful.wav
"""

from typing import Optional
from .generator import MusicGenerator
from .batch import BatchProcessor, create_sample_csv

__version__ = "1.1.0"
__all__ = ["MusicGenerator", "quick_generate", "BatchProcessor", "create_sample_csv"]


def quick_generate(
    prompt: str, 
    output_file: str, 
    duration: float = 10.0,
    model_name: str = "facebook/musicgen-small",
    temperature: float = 1.0,
    guidance_scale: float = 3.0,
    format: str = "auto",
    bitrate: str = "192k"
) -> str:
    """
    Quick one-liner to generate music and save to file.
    
    Args:
        prompt: Text description of the music to generate
        output_file: Filename to save the generated audio
        duration: Duration in seconds (0.1 to 120.0)
        model_name: HuggingFace model to use
        temperature: Sampling temperature (0.1-2.0)
        guidance_scale: Classifier-free guidance (1.0-10.0)
        format: Output format ("wav", "mp3", or "auto" to detect from filename)
        bitrate: MP3 bitrate ("128k", "192k", "256k", "320k")
    
    Returns:
        Path to the generated file
    
    Example:
        >>> quick_generate("upbeat jazz", "jazz.wav", duration=15)
        >>> quick_generate("ambient soundscape", "ambient.mp3", duration=60, format="mp3", bitrate="320k")
    """
    generator = MusicGenerator(model_name=model_name)
    
    # Auto-detect format from filename
    if format == "auto":
        if output_file.lower().endswith('.mp3'):
            format = "mp3"
        elif output_file.lower().endswith('.wav'):
            format = "wav"
        else:
            format = "wav"  # Default to WAV
    
    # Use extended generation for > 30 seconds
    if duration > 30:
        audio, sample_rate = generator.generate_extended(
            prompt=prompt,
            duration=duration,
            temperature=temperature,
            guidance_scale=guidance_scale
        )
    else:
        audio, sample_rate = generator.generate(
            prompt=prompt,
            duration=duration,
            temperature=temperature,
            guidance_scale=guidance_scale
        )
    
    # Save in specified format
    final_output = generator.save_audio_as_format(
        audio, sample_rate, output_file, format=format, bitrate=bitrate, delete_wav=(format == "mp3")
    )
    
    return final_output