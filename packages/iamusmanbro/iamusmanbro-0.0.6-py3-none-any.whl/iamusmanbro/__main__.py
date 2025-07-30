"""
iamusmanbro.__main__

Robust CLI “brand intro” for Usman Ghani.
Shows a spinning ASCII donut (if Rich is available) and prints
branding info. If anything fails, falls back to a simple text banner.
"""

import sys
import time

# ----------------------------------------------------------------------
# Try to import optional fancy deps
# ----------------------------------------------------------------------
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.live import Live
    from rich.text import Text
    from rich.align import Align
    RICH_AVAILABLE = True
except ModuleNotFoundError:  # Rich not installed
    RICH_AVAILABLE = False

# ----------------------------------------------------------------------
# Fancy animation helpers (use only if Rich is present)
# ----------------------------------------------------------------------
if RICH_AVAILABLE:

    import math

    def donut_frames(width=40, height=20):
        """Generator yielding frames of an ASCII donut."""
        A, B = 0.0, 0.0
        chars = ".,-~:;=!*#$@"
        while True:
            zbuf = [0] * (width * height)
            frame = [" "] * (width * height)
            for j in range(0, 628, 7):      # j ~= theta
                for i in range(0, 628, 2):  # i ~= phi
                    c, d = math.sin(i), math.cos(j)
                    e, f = math.sin(A), math.sin(j)
                    g, h = math.cos(A), d + 2
                    D = 1 / (c * h * e + f * g + 5)
                    l, m, n = math.cos(i), math.cos(B), math.sin(B)
                    t = c * h * g - f * e
                    x = int(width / 2 + 30 * D * (l * h * m - t * n))
                    y = int(height / 2 + 15 * D * (l * h * n + t * m))
                    idx = x + width * y
                    if 0 <= idx < width * height:
                        if D > zbuf[idx]:
                            zbuf[idx] = D
                            luminance = (
                                f * e - c * d * g - c * d * e - f * g - l * d * n
                            )
                            frame[idx] = chars[int(max(0, min(11, luminance * 8)))]
            A += 0.04
            B += 0.02
            yield "\n".join(
                "".join(frame[k : k + width]) for k in range(0, len(frame), width)
            )

# ----------------------------------------------------------------------
# Core printing functions
# ----------------------------------------------------------------------
def show_fallback_banner():
    """Simple banner if Rich or animation fails."""
    banner = r"""
*******************************************************
*        Usman Ghani – Machine‑Learning Engineer      *
*  GitHub:   https://github.com/iamusmanbro           *
*  LinkedIn: https://linkedin.com/in/iamusmanbro      *
*  PyPI:     pip install usman-ghani                  *
*******************************************************
"""
    sys.stdout.write(banner + "\n")


def show_rich_intro():
    """Fancy Rich intro with animation."""
    console = Console()
    try:
        # -------- Spinning donut (4 s) --------
        frames = donut_frames()
        with Live(Align.center(Text(next(frames)), vertical="middle"), console=console, refresh_per_second=20) as live:
            start = time.time()
            while time.time() - start < 4:
                live.update(Align.center(Text(next(frames)), vertical="middle"))

        # -------- Branding panels --------
        console.clear()
        console.print(
            Panel.fit(
                "[bold magenta]✨ Welcome to the world of Usman Ghani ✨[/bold magenta]",
                border_style="magenta",
            )
        )
        console.print(
            Panel.fit(
                "🚀 Machine‑Learning Developer\n🎯 Automation Engineer\n🧠 Python Powerhouse",
                title="[bold green]Who Am I[/bold green]",
                style="bold green",
            )
        )
        console.print(
            "\n[cyan]🔗 GitHub:[/] https://github.com/iamusmanbro\n"
            "[cyan]🔗 LinkedIn:[/] https://linkedin.com/in/iamusmanbro\n"
        )
        console.print(
            "[bold yellow]👉  Check out [bold]usman‑ghani[/bold] on PyPI "
            "for production utilities![/bold yellow]"
        )
    except Exception as exc:  # noqa: BLE001
        # Anything went wrong? show fallback + error info
        console.print(f"[red]⚠️  Animation error: {exc}[/red]")
        show_fallback_banner()


# ----------------------------------------------------------------------
# Entrypoint
# ----------------------------------------------------------------------
def main() -> None:
    if RICH_AVAILABLE:
        show_rich_intro()
    else:
        sys.stderr.write(
            "⚠️  Rich library not found. "
            "Install it with:  pip install rich  \n"
        )
        show_fallback_banner()


if __name__ == "__main__":
    main()
