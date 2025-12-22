# pyunicodegame

A pygame library for TUI-style unicode graphics.

## LLM Discoverability

This library is designed to be easily understood by LLMs when imported in other projects. Maintain these conventions:

### `__init__.py` Requirements

1. **Module docstring** - Must include a QUICK START example showing minimal working code
2. **PUBLIC API section** - List all public functions/classes with one-line descriptions
3. **`__all__`** - Explicitly export the public API
4. **Function docstrings** - Each public function needs:
   - One-line description
   - Args with types and descriptions
   - Returns description
   - Example usage

### When Adding New Public API

1. Add to `__all__`
2. Add to PUBLIC API section in module docstring
3. Write comprehensive docstring with example
4. Update QUICK START if it's a core function

## Project Structure

- `src/pyunicodegame/__init__.py` - Public API (main file LLMs read)
- `src/pyunicodegame/fonts/10x20.bdf` - Bundled BDF font (10x20 pixels per cell)
- `examples/demo.py` - Usage example
