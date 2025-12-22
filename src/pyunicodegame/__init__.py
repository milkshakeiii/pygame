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

import os
from typing import Callable, Dict, Optional, Tuple

import pygame
import pygame.freetype

__version__ = "0.1.0"
__all__ = ["init", "run", "quit", "create_window", "get_window", "remove_window", "Window"]

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
    global _root_cell_width, _root_cell_height, _clock

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
    global _running

    _running = True
    while _running:
        dt = _clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                _running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    _running = False
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

        # Composite all windows in z-order directly to display
        display = pygame.display.get_surface()
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

            display.blit(window.surface, (px, py))

        pygame.display.flip()

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
