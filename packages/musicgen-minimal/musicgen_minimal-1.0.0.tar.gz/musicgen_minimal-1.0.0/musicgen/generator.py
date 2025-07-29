"""
Core music generation functionality.
Dead simple wrapper around Facebook's MusicGen model.
"""

import logging
import time
from typing import Tuple, Optional

import numpy as np
import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration
try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    import scipy.io.wavfile as wavfile
    SOUNDFILE_AVAILABLE = False

logger = logging.getLogger(__name__)


class MusicGenerator:
    """
    Dead simple music generation that actually works.
    
    No complex abstractions, no microservices, no enterprise patterns.
    Just a thin wrapper around the working MusicGen model.
    """
    
    def __init__(self, model_name: str = "facebook/musicgen-small", device: Optional[str] = None):
        """
        Initialize the generator.
        
        Args:
            model_name: HuggingFace model name. Options:
                - facebook/musicgen-small (default, fastest)
                - facebook/musicgen-medium (better quality, slower)
                - facebook/musicgen-large (best quality, slowest)
            device: Device to use. Auto-detects if None.
        """
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        logger.info(f"Loading {model_name} on {self.device}...")
        self._load_model()
        logger.info("✓ Model loaded successfully")
        
    def _load_model(self):
        """Load the HuggingFace models with robust error handling."""
        try:
            self.processor = AutoProcessor.from_pretrained(self.model_name)
            self.model = MusicgenForConditionalGeneration.from_pretrained(self.model_name)
            self.model.to(self.device)
        except Exception as e:
            error_msg = f"Failed to load model '{self.model_name}': {e}"
            
            # Provide helpful suggestions based on common errors
            if "ConnectTimeout" in str(e) or "ConnectionError" in str(e):
                error_msg += "\n\nSuggestion: Check your internet connection. Model downloads require internet access."
            elif "OutOfMemoryError" in str(e) or "CUDA out of memory" in str(e):
                error_msg += f"\n\nSuggestion: Try using CPU instead: device='cpu', or use a smaller model like 'facebook/musicgen-small'."
            elif "does not appear to have a file named" in str(e):
                error_msg += f"\n\nSuggestion: Verify the model name. Available models: facebook/musicgen-small, facebook/musicgen-medium, facebook/musicgen-large"
            
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
    def generate(
        self, 
        prompt: str, 
        duration: float = 10.0, 
        temperature: float = 1.0, 
        guidance_scale: float = 3.0,
        max_new_tokens: Optional[int] = None
    ) -> Tuple[np.ndarray, int]:
        """
        Generate music from text prompt.
        
        Args:
            prompt: Text description of the music to generate
            duration: Duration in seconds (0.1 to 120.0)
            temperature: Sampling temperature (0.1-2.0, higher = more random)
            guidance_scale: Classifier-free guidance (1.0-10.0, higher = follows prompt better)
            max_new_tokens: Override automatic token calculation
            
        Returns:
            Tuple of (audio_array, sample_rate)
            
        Raises:
            ValueError: If parameters are out of valid ranges
            RuntimeError: If generation fails
        """
        # Input validation
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        if not (0.1 <= duration <= 120.0):
            raise ValueError(f"Duration must be between 0.1 and 120.0 seconds, got {duration}")
        
        if not (0.1 <= temperature <= 2.0):
            raise ValueError(f"Temperature must be between 0.1 and 2.0, got {temperature}")
        
        if not (1.0 <= guidance_scale <= 10.0):
            raise ValueError(f"Guidance scale must be between 1.0 and 10.0, got {guidance_scale}")
        
        logger.info(f"Generating: '{prompt}' for {duration}s")
        start_time = time.time()
        
        # Process the text prompt
        inputs = self.processor(
            text=[prompt],
            padding=True,
            return_tensors="pt"
        ).to(self.device)
        
        # Calculate tokens needed (roughly 256 tokens = 5 seconds)
        if max_new_tokens is None:
            max_new_tokens = int(256 * duration / 5)
        
        # Generate audio
        with torch.no_grad():
            audio_values = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=temperature,
                guidance_scale=guidance_scale
            )
        
        # Extract audio array
        audio = audio_values[0, 0].cpu().numpy()
        sample_rate = self.model.config.audio_encoder.sampling_rate
        
        generation_time = time.time() - start_time
        actual_duration = len(audio) / sample_rate
        
        logger.info(
            f"✓ Generated {actual_duration:.1f}s in {generation_time:.1f}s "
            f"({actual_duration/generation_time:.2f}x realtime)"
        )
        
        return audio, sample_rate
    
    def save_audio(self, audio: np.ndarray, sample_rate: int, filename: str):
        """
        Save audio array to WAV file.
        
        Args:
            audio: Audio array from generate()
            sample_rate: Sample rate from generate()
            filename: Output filename (.wav recommended)
        """
        # Normalize audio to prevent clipping
        audio = np.clip(audio, -1, 1)
        
        try:
            if SOUNDFILE_AVAILABLE:
                # Use soundfile for better quality and error handling
                sf.write(filename, audio, sample_rate, subtype='PCM_16')
            else:
                # Fallback to scipy
                audio_16bit = (audio * 32767).astype(np.int16)
                wavfile.write(filename, sample_rate, audio_16bit)
        except Exception as e:
            logger.error(f"Failed to save audio to {filename}: {e}")
            raise RuntimeError(f"Audio save failed: {e}")
        
        # Calculate file info
        file_size = len(audio) * 2 / 1024  # Approximate KB for 16-bit
        duration = len(audio) / sample_rate
        
        logger.info(f"✓ Saved {duration:.1f}s audio to {filename} ({file_size:.1f} KB)")
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model."""
        return {
            "model_name": self.model_name,
            "device": str(self.device),
            "sample_rate": self.model.config.audio_encoder.sampling_rate,
            "audio_channels": self.model.config.audio_encoder.audio_channels,
            "vocab_size": self.model.config.decoder.vocab_size,
        }