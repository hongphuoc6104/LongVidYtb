"""Video Renderer Engine package."""

try:
    from sys.render_cli import render_standalone
except ImportError:
    try:
        from render_cli import render_standalone
    except ImportError:
        from ..render_cli import render_standalone

__all__ = ["render_standalone"]
