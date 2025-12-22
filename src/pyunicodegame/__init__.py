"""
pyunicodegame - A pygame library for TUI-style unicode graphics.

QUICK START:
    import pyunicodegame

    def update(dt):
        pass  # Game logic here

    def render():
        root = pyunicodegame.get_window("root")
        root.put(10, 5, "@", (0, 255, 0))

    def on_key(key):
        pass  # Handle key presses here

    pyunicodegame.init("My Game", width=80, height=25, bg=(20, 20, 30, 255))
    pyunicodegame.run(update=update, render=render, on_key=on_key)

PUBLIC API:
    init(title, width, height, bg) - Initialize pygame, create root window, return it
    run(update, render, on_key) - Run the main game loop
    quit() - Signal the game loop to exit
    create_window(name, x, y, width, height, ...) - Create a named window
    get_window(name) - Get a window by name ("root" is auto-created)
    remove_window(name) - Remove a window
"""

import math
import os
from typing import Callable, Dict, List, Optional, Tuple

import pygame
import pygame.freetype

__version__ = "0.1.0"
__all__ = [
    "init", "run", "quit",
    "create_window", "get_window", "remove_window", "Window",
    "Sprite", "SpriteFrame", "create_sprite",
    "EffectSprite", "create_effect",
]

# Font configuration
FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
AVAILABLE_FONTS = {
    "6x13": "6x13.bdf",
    "9x18": "9x18.bdf",
    "10x20": "10x20.bdf",
}
DEFAULT_FONT = "10x20"

# Module state
_fonts: Dict[str, pygame.freetype.Font] = {}
_font_dimensions: Dict[str, Tuple[int, int]] = {}
_root_cell_width: int = 0
_root_cell_height: int = 0
_running: bool = False
_clock: pygame.time.Clock = None
_windows: Dict[str, "Window"] = {}
_fullscreen: bool = False
_windowed_size: Tuple[int, int] = (0, 0)  # Original window size for restoring
_render_surface: pygame.Surface = None  # Off-screen surface for fullscreen scaling


def _get_font_dimensions(font: pygame.freetype.Font) -> Tuple[int, int]:
    """Get cell dimensions by rendering a test character."""
    surf, _ = font.render("\u2588", (255, 255, 255))  # Full block character
    return surf.get_width(), surf.get_height()


def _load_font(font_name: str) -> pygame.freetype.Font:
    """Load a font by name, caching for reuse."""
    if font_name in _fonts:
        return _fonts[font_name]

    if font_name not in AVAILABLE_FONTS:
        raise ValueError(f"Unknown font: {font_name}. Available: {list(AVAILABLE_FONTS.keys())}")

    font_path = os.path.join(FONT_DIR, AVAILABLE_FONTS[font_name])
    font = pygame.freetype.Font(font_path)
    _fonts[font_name] = font
    _font_dimensions[font_name] = _get_font_dimensions(font)
    return font


def _toggle_fullscreen() -> None:
    """Toggle between windowed and fullscreen mode, preserving aspect ratio."""
    global _fullscreen, _windowed_size, _render_surface

    _fullscreen = not _fullscreen

    if _fullscreen:
        # Save current window size
        _windowed_size = _render_surface.get_size()

        # Get desktop resolution
        info = pygame.display.Info()
        screen_w, screen_h = info.current_w, info.current_h

        # Switch to fullscreen
        pygame.display.set_mode((screen_w, screen_h), pygame.FULLSCREEN)
    else:
        # Restore windowed mode
        pygame.display.set_mode(_windowed_size)


class Window:
    """
    A rendering surface with its own coordinate system and font.

    Windows are composited in z_index order onto the main screen.
    Each window can have a different font size for parallax effects.

    Attributes:
        name: Unique identifier for this window
        x: X position in root cell coordinates
        y: Y position in root cell coordinates
        width: Width in this window's cells
        height: Height in this window's cells
        z_index: Drawing order (higher = on top)
        alpha: Transparency (0-255)
        visible: Whether to draw this window
    """

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        width: int,
        height: int,
        z_index: int = 0,
        font_name: str = DEFAULT_FONT,
        scale: float = 1.0,
        alpha: int = 255,
        bg: Optional[Tuple[int, int, int, int]] = None,
    ):
        self.name = name
        self.x = x  # Root cell coordinates
        self.y = y
        self.width = width  # In this window's cells
        self.height = height
        self.z_index = z_index
        self.alpha = alpha
        self.scale = scale
        self.visible = True
        self._bg = bg if bg is not None else (0, 0, 0, 0)  # Default transparent
        self._sprites: List["Sprite"] = []

        # Load font and get dimensions
        self._font = _load_font(font_name)
        self._font_name = font_name
        self._cell_width, self._cell_height = _font_dimensions[font_name]

        # Apply scale
        self._cell_width = int(self._cell_width * scale)
        self._cell_height = int(self._cell_height * scale)

        # Create surface
        pixel_width = width * self._cell_width
        pixel_height = height * self._cell_height
        self.surface = pygame.Surface((pixel_width, pixel_height), pygame.SRCALPHA)
        self.surface.fill(self._bg)

    def set_bg(self, color: Tuple[int, int, int, int]) -> None:
        """Set the background color (R, G, B, A)."""
        self._bg = color

    def put(
        self,
        x: int,
        y: int,
        char: str,
        fg: Tuple[int, int, int] = (255, 255, 255),
        bg: Optional[Tuple[int, int, int]] = None,
    ) -> None:
        """
        Draw a character at cell position (x, y).

        Args:
            x: Cell column
            y: Cell row
            char: Character to draw
            fg: Foreground color (R, G, B)
            bg: Background color (R, G, B) or None for transparent
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return

        px = x * self._cell_width
        py = y * self._cell_height

        # Draw background if specified
        if bg is not None:
            rect = pygame.Rect(px, py, self._cell_width, self._cell_height)
            self.surface.fill((*bg, 255), rect)

        # Render character
        if self.scale != 1.0:
            # Render at native size then scale
            surf, _ = self._font.render(char, fg)
            surf = pygame.transform.scale(surf, (self._cell_width, self._cell_height))
        else:
            surf, _ = self._font.render(char, fg)

        self.surface.blit(surf, (px, py))

    def put_string(
        self,
        x: int,
        y: int,
        text: str,
        fg: Tuple[int, int, int] = (255, 255, 255),
        bg: Optional[Tuple[int, int, int]] = None,
    ) -> None:
        """
        Draw a string starting at cell position (x, y).

        Args:
            x: Starting cell column
            y: Cell row
            text: String to draw
            fg: Foreground color
            bg: Background color or None
        """
        for i, char in enumerate(text):
            self.put(x + i, y, char, fg, bg)

    def _put_at_pixel(
        self,
        px: float,
        py: float,
        char: str,
        fg: Tuple[int, int, int],
        bg: Optional[Tuple[int, int, int, int]] = None,
        alpha: int = 255,
    ) -> None:
        """Draw a character at exact pixel coordinates (for sprite interpolation)."""
        px_int = int(px)
        py_int = int(py)

        # Bounds check
        if (px_int < 0 or py_int < 0 or
            px_int >= self.surface.get_width() or py_int >= self.surface.get_height()):
            return

        # Draw background if specified
        if bg is not None:
            rect = pygame.Rect(px_int, py_int, self._cell_width, self._cell_height)
            # Apply alpha to background
            bg_with_alpha = (bg[0], bg[1], bg[2], int(bg[3] * alpha / 255) if len(bg) > 3 else alpha)
            self.surface.fill(bg_with_alpha, rect)

        # Render character
        if self.scale != 1.0:
            surf, _ = self._font.render(char, fg)
            surf = pygame.transform.scale(surf, (self._cell_width, self._cell_height))
        else:
            surf, _ = self._font.render(char, fg)

        # Apply alpha to the character surface
        if alpha < 255:
            surf.set_alpha(alpha)

        self.surface.blit(surf, (px_int, py_int))

    def add_sprite(self, sprite: "Sprite") -> "Sprite":
        """Add a sprite to this window. Returns the sprite for chaining."""
        self._sprites.append(sprite)
        return sprite

    def remove_sprite(self, sprite: "Sprite") -> None:
        """Remove a sprite from this window."""
        if sprite in self._sprites:
            self._sprites.remove(sprite)

    def update_sprites(self, dt: float) -> None:
        """Update all sprite positions and remove dead EffectSprites."""
        for sprite in self._sprites:
            sprite.update(dt, self._cell_width, self._cell_height)

        # Remove dead EffectSprites
        self._sprites = [s for s in self._sprites
                         if not (hasattr(s, 'alive') and not s.alive)]

    def draw_sprites(self) -> None:
        """Draw all visible sprites to this window (call this in your render function)."""
        for sprite in self._sprites:
            if sprite.visible:
                sprite.draw(self)


class SpriteFrame:
    """
    A single frame of a sprite animation.

    Contains a 2D grid of characters and optional per-character colors.
    """

    def __init__(
        self,
        chars: List[List[str]],
        fg_colors: Optional[List[List[Optional[Tuple[int, int, int]]]]] = None,
        bg_colors: Optional[List[List[Optional[Tuple[int, int, int, int]]]]] = None,
    ):
        """
        Create a sprite frame.

        Args:
            chars: 2D grid of characters (list of rows)
            fg_colors: Optional per-character foreground colors (None = use sprite default)
            bg_colors: Optional per-character background colors (None = use sprite default)
        """
        self.chars = chars
        self.fg_colors = fg_colors
        self.bg_colors = bg_colors
        self.height = len(chars)
        self.width = len(chars[0]) if chars else 0


class Sprite:
    """
    A unicode sprite - a block of characters that moves as a unit.

    Sprites support smooth movement between cells via interpolation.
    The logical position (x, y) changes instantly on move_to(), while
    the visual position smoothly interpolates toward it.
    """

    def __init__(
        self,
        frames: List[SpriteFrame],
        fg: Tuple[int, int, int] = (255, 255, 255),
        bg: Optional[Tuple[int, int, int, int]] = None,
        origin: Tuple[int, int] = (0, 0),
    ):
        """
        Create a sprite.

        Args:
            frames: List of SpriteFrame objects for animation
            fg: Default foreground color for all characters
            bg: Default background color (None = transparent)
            origin: Offset for positioning (0,0 = top-left of sprite)
        """
        self.frames = frames
        self.fg = fg
        self.bg = bg
        self.origin = origin
        self.current_frame = 0
        self.frame_timer = 0.0
        self.frame_duration = 0.1  # Seconds per frame (for future animation)
        self.visible = True

        # Logical position (changes instantly on move_to)
        self.x = 0
        self.y = 0

        # Visual position (private, interpolates toward logical)
        self._visual_x = 0.0  # In pixels
        self._visual_y = 0.0
        self._move_speed = 0.0  # Cells per second (0 = instant)

    def move_to(self, x: int, y: int) -> None:
        """
        Move the sprite to a new logical position.

        The logical position changes instantly. The visual position
        will interpolate toward it based on _move_speed.
        """
        self.x = x
        self.y = y

    def update(self, dt: float, cell_width: int, cell_height: int) -> None:
        """
        Update the sprite's visual position (called by Window.update_sprites).

        Args:
            dt: Delta time in seconds
            cell_width: Width of a cell in pixels
            cell_height: Height of a cell in pixels
        """
        # Target is logical position in pixels
        target_px = self.x * cell_width
        target_py = self.y * cell_height

        if self._move_speed <= 0:
            # Instant movement
            self._visual_x = float(target_px)
            self._visual_y = float(target_py)
            return

        dx = target_px - self._visual_x
        dy = target_py - self._visual_y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0.5:  # Small threshold to avoid jitter
            speed_px = self._move_speed * cell_width  # cells/sec -> pixels/sec
            move_dist = min(speed_px * dt, distance)
            self._visual_x += (dx / distance) * move_dist
            self._visual_y += (dy / distance) * move_dist
        else:
            self._visual_x = float(target_px)
            self._visual_y = float(target_py)

    def draw(self, window: "Window") -> None:
        """Draw the sprite to a window at its visual position."""
        if not self.frames:
            return

        frame = self.frames[self.current_frame]

        # Calculate pixel position (visual, not logical)
        base_px = self._visual_x - self.origin[0] * window._cell_width
        base_py = self._visual_y - self.origin[1] * window._cell_height

        for row_idx, row in enumerate(frame.chars):
            for col_idx, char in enumerate(row):
                if char == ' ':
                    continue  # Transparent

                px = base_px + col_idx * window._cell_width
                py = base_py + row_idx * window._cell_height

                # Determine colors
                fg = self.fg
                if frame.fg_colors and row_idx < len(frame.fg_colors):
                    row_colors = frame.fg_colors[row_idx]
                    if col_idx < len(row_colors) and row_colors[col_idx] is not None:
                        fg = row_colors[col_idx]

                bg = self.bg
                if frame.bg_colors and row_idx < len(frame.bg_colors):
                    row_colors = frame.bg_colors[row_idx]
                    if col_idx < len(row_colors) and row_colors[col_idx] is not None:
                        bg = row_colors[col_idx]

                window._put_at_pixel(px, py, char, fg, bg)


class EffectSprite:
    """
    A visual-only sprite for effects (particles, sparks, explosions, etc.).

    Unlike Sprite, EffectSprite has no logical position - only visual.
    It uses velocity-based movement with optional drag and fade.

    Attributes:
        x, y: Position in cells (float for smooth movement)
        vx, vy: Velocity in cells per second
        drag: Velocity decay per second (0.1 = decays to 10% after 1 sec, 1.0 = no drag)
        fade_time: Seconds until fully transparent (0 = no fade)
        alive: False when fully faded (will be auto-removed from window)
    """

    def __init__(
        self,
        frames: List[SpriteFrame],
        fg: Tuple[int, int, int] = (255, 255, 255),
        bg: Optional[Tuple[int, int, int, int]] = None,
        origin: Tuple[int, int] = (0, 0),
    ):
        self.frames = frames
        self.fg = fg
        self.bg = bg
        self.origin = origin
        self.current_frame = 0
        self.visible = True
        self.alive = True

        # Position in cells (float for smooth movement)
        self.x = 0.0
        self.y = 0.0

        # Velocity in cells per second
        self.vx = 0.0
        self.vy = 0.0

        # Drag: velocity multiplier per second (0.1 = decays to 10% after 1 sec)
        self.drag = 1.0  # 1.0 = no drag

        # Fade: seconds until fully transparent (0 = no fade)
        self.fade_time = 0.0
        self._fade_elapsed = 0.0
        self._initial_alpha = 255

    def update(self, dt: float, cell_width: int, cell_height: int) -> None:
        """Update position, velocity, and fade."""
        if not self.alive:
            return

        # Apply velocity
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Apply drag (frame-rate independent exponential decay)
        if self.drag < 1.0 and self.drag > 0:
            decay = self.drag ** dt
            self.vx *= decay
            self.vy *= decay

        # Apply fade
        if self.fade_time > 0:
            self._fade_elapsed += dt
            if self._fade_elapsed >= self.fade_time:
                self.alive = False
                self.visible = False

    def draw(self, window: "Window") -> None:
        """Draw the effect sprite with current alpha."""
        if not self.frames or not self.visible:
            return

        # Calculate current alpha based on fade progress
        alpha = self._initial_alpha
        if self.fade_time > 0:
            fade_progress = min(1.0, self._fade_elapsed / self.fade_time)
            alpha = int(self._initial_alpha * (1.0 - fade_progress))

        frame = self.frames[self.current_frame]
        base_px = self.x * window._cell_width - self.origin[0] * window._cell_width
        base_py = self.y * window._cell_height - self.origin[1] * window._cell_height

        for row_idx, row in enumerate(frame.chars):
            for col_idx, char in enumerate(row):
                if char == ' ':
                    continue

                px = base_px + col_idx * window._cell_width
                py = base_py + row_idx * window._cell_height

                # Determine colors
                fg = self.fg
                if frame.fg_colors and row_idx < len(frame.fg_colors):
                    row_colors = frame.fg_colors[row_idx]
                    if col_idx < len(row_colors) and row_colors[col_idx] is not None:
                        fg = row_colors[col_idx]

                bg = self.bg
                if frame.bg_colors and row_idx < len(frame.bg_colors):
                    row_colors = frame.bg_colors[row_idx]
                    if col_idx < len(row_colors) and row_colors[col_idx] is not None:
                        bg = row_colors[col_idx]

                window._put_at_pixel(px, py, char, fg, bg, alpha=alpha)


def create_sprite(
    pattern: str,
    fg: Tuple[int, int, int] = (255, 255, 255),
    bg: Optional[Tuple[int, int, int, int]] = None,
    char_colors: Optional[Dict[str, Tuple[int, int, int]]] = None,
) -> Sprite:
    """
    Create a single-frame sprite from a multi-line string pattern.

    Args:
        pattern: Multi-line string defining the sprite shape.
                 Spaces are transparent. Leading/trailing blank lines are trimmed.
        fg: Default foreground color for all characters
        bg: Default background color (None = transparent)
        char_colors: Optional dict mapping characters to foreground colors

    Returns:
        A new Sprite object

    Example:
        player = pyunicodegame.create_sprite('''
            @
           /|\\
           / \\
        ''', fg=(0, 255, 0), char_colors={'@': (255, 255, 0)})
    """
    # Parse pattern into lines, stripping common leading whitespace
    lines = pattern.split('\n')

    # Remove empty leading/trailing lines
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    if not lines:
        return Sprite([SpriteFrame([[]])], fg, bg)

    # Find minimum leading whitespace (excluding empty lines)
    min_indent = float('inf')
    for line in lines:
        if line.strip():
            indent = len(line) - len(line.lstrip())
            min_indent = min(min_indent, indent)

    if min_indent == float('inf'):
        min_indent = 0

    # Strip common indent and build char grid
    chars = []
    fg_colors = [] if char_colors else None

    max_width = 0
    for line in lines:
        # Remove common indent
        if len(line) >= min_indent:
            line = line[int(min_indent):]
        else:
            line = ''

        row = list(line)
        chars.append(row)
        max_width = max(max_width, len(row))

        if char_colors:
            color_row = []
            for c in row:
                color_row.append(char_colors.get(c))
            fg_colors.append(color_row)

    # Pad rows to same width
    for row in chars:
        while len(row) < max_width:
            row.append(' ')

    if fg_colors:
        for row in fg_colors:
            while len(row) < max_width:
                row.append(None)

    frame = SpriteFrame(chars, fg_colors)
    return Sprite([frame], fg, bg)


def create_effect(
    pattern: str,
    x: float,
    y: float,
    vx: float = 0.0,
    vy: float = 0.0,
    fg: Tuple[int, int, int] = (255, 255, 255),
    bg: Optional[Tuple[int, int, int, int]] = None,
    drag: float = 1.0,
    fade_time: float = 0.0,
    char_colors: Optional[Dict[str, Tuple[int, int, int]]] = None,
) -> EffectSprite:
    """
    Create an effect sprite with velocity, drag, and fade.

    Args:
        pattern: Character(s) for the effect (multi-line string supported)
        x, y: Starting position in cells
        vx, vy: Velocity in cells per second
        fg: Foreground color
        bg: Background color (None = transparent)
        drag: Velocity decay per second (0.1 = decays to 10%/sec, 1.0 = no drag)
        fade_time: Seconds until fully transparent (0 = no fade)
        char_colors: Optional per-character color overrides

    Returns:
        An EffectSprite ready to add to a window

    Example:
        # Create a spark that flies up-right, slows down, and fades out
        spark = pyunicodegame.create_effect('*', x=10, y=15, vx=5, vy=-8,
                                            fg=(255, 200, 0), drag=0.3, fade_time=0.5)
        window.add_sprite(spark)
    """
    # Reuse create_sprite's pattern parsing logic
    lines = pattern.split('\n')

    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    if not lines:
        effect = EffectSprite([SpriteFrame([[]])], fg, bg)
        effect.x = x
        effect.y = y
        return effect

    min_indent = float('inf')
    for line in lines:
        if line.strip():
            indent = len(line) - len(line.lstrip())
            min_indent = min(min_indent, indent)

    if min_indent == float('inf'):
        min_indent = 0

    chars = []
    fg_colors = [] if char_colors else None
    max_width = 0

    for line in lines:
        if len(line) >= min_indent:
            line = line[int(min_indent):]
        else:
            line = ''

        row = list(line)
        chars.append(row)
        max_width = max(max_width, len(row))

        if char_colors:
            color_row = []
            for c in row:
                color_row.append(char_colors.get(c))
            fg_colors.append(color_row)

    for row in chars:
        while len(row) < max_width:
            row.append(' ')

    if fg_colors:
        for row in fg_colors:
            while len(row) < max_width:
                row.append(None)

    frame = SpriteFrame(chars, fg_colors)
    effect = EffectSprite([frame], fg, bg)
    effect.x = x
    effect.y = y
    effect.vx = vx
    effect.vy = vy
    effect.drag = drag
    effect.fade_time = fade_time
    return effect


def init(
    title: str,
    width: int = 80,
    height: int = 25,
    bg: Optional[Tuple[int, int, int, int]] = None,
) -> "Window":
    """
    Initialize pyunicodegame and pygame, creating a window sized for unicode cells.

    Each cell is 10x20 pixels (from the bundled BDF font). So width=80, height=25
    creates an 800x500 pixel window.

    A root window is automatically created that fills the screen.

    Args:
        title: Window title displayed in the title bar
        width: Grid width in unicode cells (default 80)
        height: Grid height in unicode cells (default 25)
        bg: Root window background color (R, G, B, A), default transparent

    Returns:
        The root Window object

    Example:
        root = pyunicodegame.init("My Game", width=80, height=30, bg=(20, 20, 30, 255))
        # root is now available, or use pyunicodegame.get_window("root")
    """
    global _root_cell_width, _root_cell_height, _clock, _render_surface, _windowed_size

    pygame.init()
    pygame.freetype.init()

    # Load root font and get cell dimensions
    _load_font(DEFAULT_FONT)
    _root_cell_width, _root_cell_height = _font_dimensions[DEFAULT_FONT]

    # Create pygame display
    pixel_width = width * _root_cell_width
    pixel_height = height * _root_cell_height
    pygame.display.set_mode((pixel_width, pixel_height))
    pygame.display.set_caption(title)

    # Create off-screen render surface (used for fullscreen scaling)
    _render_surface = pygame.Surface((pixel_width, pixel_height))
    _windowed_size = (pixel_width, pixel_height)

    _clock = pygame.time.Clock()

    # Create root window automatically
    root = create_window("root", 0, 0, width, height, z_index=0, bg=bg)
    return root


def create_window(
    name: str,
    x: int,
    y: int,
    width: int,
    height: int,
    z_index: int = 0,
    font_name: str = DEFAULT_FONT,
    scale: float = 1.0,
    alpha: int = 255,
    bg: Optional[Tuple[int, int, int, int]] = None,
) -> "Window":
    """
    Create a named window for rendering.

    Args:
        name: Unique identifier for this window
        x: X position in root cell coordinates
        y: Y position in root cell coordinates
        width: Width in this window's cells
        height: Height in this window's cells
        z_index: Drawing order (higher = on top, default 0)
        font_name: Font to use ("6x13", "9x18", "10x20")
        scale: Additional scaling factor (default 1.0)
        alpha: Transparency 0-255 (default 255 = opaque)
        bg: Background color (R, G, B, A), default transparent

    Returns:
        The created Window object

    Example:
        # Create a background layer with large font
        pyunicodegame.create_window("bg", 0, 0, 40, 15, z_index=0, font_name="10x20", alpha=128)

        # Create a foreground layer with small font
        pyunicodegame.create_window("fg", 0, 0, 80, 30, z_index=10, font_name="6x13")
    """
    window = Window(name, x, y, width, height, z_index, font_name, scale, alpha, bg)
    _windows[name] = window
    return window


def get_window(name: str) -> "Window":
    """
    Get a window by name.

    Args:
        name: The window's unique identifier

    Returns:
        The Window object

    Raises:
        KeyError: If no window with that name exists
    """
    return _windows[name]


def remove_window(name: str) -> None:
    """
    Remove a window by name.

    Args:
        name: The window's unique identifier
    """
    if name in _windows:
        del _windows[name]


def run(
    update: Optional[Callable[[float], None]] = None,
    render: Optional[Callable[[], None]] = None,
    on_key: Optional[Callable[[int], None]] = None,
) -> None:
    """
    Run the main game loop.

    Handles events, calls update/render callbacks, and manages timing.
    Loop exits on window close, Escape key, or when quit() is called.

    Built-in controls:
        - Escape: Exit the game
        - Alt+Enter (Option+Enter on Mac): Toggle fullscreen (aspect-ratio preserved)

    Args:
        update: Called each frame with dt (seconds since last frame)
        render: Called each frame to draw
        on_key: Called when a key is pressed, with the pygame key code

    Example:
        def update(dt):
            player.move(dt)

        def render():
            win = pyunicodegame.get_window("main")
            win.clear()
            win.put(10, 5, "@", (0, 255, 0))

        def on_key(key):
            if key == pygame.K_SPACE:
                player.jump()

        pyunicodegame.run(update=update, render=render, on_key=on_key)
    """
    global _running, _fullscreen

    _running = True
    while _running:
        dt = _clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                _running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    _running = False
                elif event.key == pygame.K_RETURN and (event.mod & pygame.KMOD_ALT):
                    # Alt+Enter (Option+Enter on Mac) toggles fullscreen
                    _toggle_fullscreen()
                elif on_key:
                    on_key(event.key)

        if update:
            update(dt)

        # Clear all windows to their background color
        for window in _windows.values():
            window.surface.fill(window._bg)

        # Call render callback (client draws to windows)
        if render:
            render()

        # Composite all windows in z-order to render surface
        _render_surface.fill((0, 0, 0))
        sorted_windows = sorted(_windows.values(), key=lambda w: w.z_index)
        for window in sorted_windows:
            if not window.visible:
                continue

            # Convert root cell coords to pixels
            px = window.x * _root_cell_width
            py = window.y * _root_cell_height

            # Apply alpha
            if window.alpha < 255:
                window.surface.set_alpha(window.alpha)

            _render_surface.blit(window.surface, (px, py))

        # Blit render surface to display (with scaling in fullscreen)
        display = pygame.display.get_surface()
        if _fullscreen:
            # Scale to fit display while preserving aspect ratio (letterbox/pillarbox)
            display.fill((0, 0, 0))
            src_w, src_h = _render_surface.get_size()
            dst_w, dst_h = display.get_size()

            # Calculate scaling factor
            scale = min(dst_w / src_w, dst_h / src_h)
            scaled_w = int(src_w * scale)
            scaled_h = int(src_h * scale)

            # Center on screen
            offset_x = (dst_w - scaled_w) // 2
            offset_y = (dst_h - scaled_h) // 2

            scaled = pygame.transform.scale(_render_surface, (scaled_w, scaled_h))
            display.blit(scaled, (offset_x, offset_y))
        else:
            display.blit(_render_surface, (0, 0))

        pygame.display.flip()

    # Reset fullscreen state
    _fullscreen = False

    pygame.quit()


def quit() -> None:
    """
    Signal the game loop to exit.

    Call this from within update or on_key to stop the game.

    Example:
        def on_key(key):
            if key == pygame.K_q:
                pyunicodegame.quit()
    """
    global _running
    _running = False
