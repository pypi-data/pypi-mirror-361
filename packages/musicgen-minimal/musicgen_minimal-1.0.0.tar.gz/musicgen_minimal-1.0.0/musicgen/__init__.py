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

__version__ = "1.0.0"
__all__ = ["MusicGenerator", "quick_generate"]


def quick_generate(
    prompt: str, 
    output_file: str, 
    duration: float = 10.0,
    model_name: str = "facebook/musicgen-small",
    temperature: float = 1.0,
    guidance_scale: float = 3.0
) -> None:
    """
    Quick one-liner to generate music and save to file.
    
    Args:
        prompt: Text description of the music to generate
        output_file: Filename to save the generated audio
        duration: Duration in seconds (0.1 to 120.0)
        model_name: HuggingFace model to use
        temperature: Sampling temperature (0.1-2.0)
        guidance_scale: Classifier-free guidance (1.0-10.0)
    
    Example:
        >>> quick_generate("upbeat jazz", "jazz.wav", duration=15)
    """
    generator = MusicGenerator(model_name=model_name)
    audio, sample_rate = generator.generate(
        prompt=prompt,
        duration=duration,
        temperature=temperature,
        guidance_scale=guidance_scale
    )
    generator.save_audio(audio, sample_rate, output_file)