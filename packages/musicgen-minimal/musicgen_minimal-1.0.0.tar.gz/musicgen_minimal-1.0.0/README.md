# MusicGen Minimal

**Simple text-to-music generation that actually works.**

This is a dead-simple wrapper around Facebook's MusicGen model. No enterprise architecture, no microservices, no broken abstractions. Just 300 lines of Python that generate music from text.

## What It Does

- ✅ **Generates music from text prompts** - "upbeat jazz piano" → actual audio
- ✅ **Works out of the box** - No complex configuration required
- ✅ **Supports multiple model sizes** - Small (fast), Medium (better), Large (best)
- ✅ **Simple CLI and Python API** - Both just work
- ✅ **Saves to standard WAV files** - Compatible with everything

## What It Doesn't Do

- ❌ **No real-time streaming** - Generation takes time (0.1-0.3x realtime)
- ❌ **No multi-instrument separation** - Single audio track output
- ❌ **No editing or post-processing** - Use Audacity or similar tools
- ❌ **No web interface** - CLI and Python API only
- ❌ **No authentication or user management** - Just generates music

## Installation

```bash
pip install musicgen-minimal
```

Or from source:
```bash
git clone https://github.com/example/musicgen-minimal.git
cd musicgen-minimal
pip install -e .
```

### Requirements

- Python 3.8+
- 4GB+ RAM (8GB+ recommended)
- Internet connection (for model download)
- Optional: CUDA GPU (much faster)

## Quick Start

### Command Line

```bash
# Generate 10 seconds of music
musicgen generate "upbeat jazz piano with walking bass" -o jazz.wav

# Longer duration with specific model
musicgen generate "peaceful ambient forest sounds" -d 30 -m medium -o ambient.wav

# Check system info
musicgen info

# Test everything works
musicgen test
```

### Python API

```python
from musicgen import MusicGenerator

# Create generator
generator = MusicGenerator()

# Generate music
audio, sample_rate = generator.generate(
    "energetic rock guitar solo", 
    duration=15.0,
    temperature=1.0,
    guidance_scale=3.0
)

# Save to file
generator.save_audio(audio, sample_rate, "rock_solo.wav")
```

## Model Options

| Model | Size | Speed | Quality | Memory |
|-------|------|--------|---------|--------|
| `small` | 300M | Fastest | Good | 2GB |
| `medium` | 1.5B | Medium | Better | 6GB |
| `large` | 3.3B | Slowest | Best | 12GB |

## Performance

**Realistic expectations (tested on CPU):**

- **Model loading**: 10-30 seconds
- **Generation speed**: 0.1-0.3x realtime
- **10 second clip**: ~30-60 seconds to generate
- **30 second clip**: ~2-3 minutes to generate

**With GPU (CUDA):**
- **Generation speed**: 0.5-1.0x realtime  
- **10 second clip**: ~10-20 seconds to generate

## CLI Reference

```bash
musicgen generate [PROMPT] [OPTIONS]

Options:
  -o, --output TEXT       Output file (default: output.wav)
  -d, --duration FLOAT    Duration in seconds (default: 10.0)
  -m, --model TEXT        Model size: small/medium/large (default: small)
  -t, --temperature FLOAT Randomness: 0.1-2.0 (default: 1.0)
  -g, --guidance FLOAT    Prompt adherence: 1.0-10.0 (default: 3.0)
  --device TEXT           Device: cpu/cuda/auto (default: auto)
  -v, --verbose           Show detailed output
```

## Python API Reference

### MusicGenerator

```python
generator = MusicGenerator(
    model_name="facebook/musicgen-small",  # or medium/large
    device=None  # auto-detect
)

audio, sample_rate = generator.generate(
    prompt="your text here",
    duration=10.0,              # seconds
    temperature=1.0,            # 0.1-2.0, higher = more random
    guidance_scale=3.0,         # 1.0-10.0, higher = follows prompt better
    max_new_tokens=None         # override automatic calculation
)

generator.save_audio(audio, sample_rate, "output.wav")

info = generator.get_model_info()  # model details
```

## Examples

### Good Prompts
- "upbeat jazz piano with walking bass"
- "peaceful ambient forest sounds with birds"
- "energetic rock guitar solo in E minor"
- "classical string quartet, melancholic"
- "electronic dance music, 120 bpm"

### Tips
- Be specific about instruments and style
- Include mood/energy level
- Mention tempo if important
- Keep it under 10-15 words

## Troubleshooting

### "Out of memory" errors
- Use smaller model: `--model small`
- Reduce duration: `--duration 5`
- Use CPU: `--device cpu`

### Slow generation
- This is normal - music generation is computationally intensive
- Use GPU if available
- Try smaller model for faster results

### Poor quality output
- Try larger model: `--model medium` or `--model large`
- Adjust guidance scale: `--guidance 5.0`
- Be more specific in prompts

### Model download issues
- Ensure internet connection
- Check available disk space (models are 1-5GB)
- Try different model size

## Limitations

1. **Generation Speed**: Not real-time (0.1-1.0x realtime depending on hardware)
2. **Duration Limits**: Longer clips (>60s) may have quality degradation
3. **Prompt Understanding**: Works best with simple, clear descriptions
4. **Audio Quality**: 32kHz mono output (good but not studio-quality)
5. **No Editing**: Generate-only, no modification of existing audio

## License

MIT License - see LICENSE file.

## Credits

- Built on Facebook's MusicGen model
- Uses HuggingFace Transformers
- Inspired by the need for simple tools that actually work

## Why This Exists

This package exists because:

1. The original MusicGen implementations are often complex or broken
2. Simple use cases don't need enterprise architecture
3. Sometimes you just want to generate music from text without setting up a full ML pipeline

**This is the music generation tool that just works.**