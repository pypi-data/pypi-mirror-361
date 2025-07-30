
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from time import sleep
import math, itertools

console = Console()

def donut_frames(width=40, height=20, R1=10, R2=4, K2=30):
    """Yield frames of ASCII donut based on classic torus algorithm."""
    A, B = 0.0, 0.0
    while True:
        output = [[" " for _ in range(width)] for _ in range(height)]
        zbuffer = [[0 for _ in range(width)] for _ in range(height)]
        cosA, sinA = math.cos(A), math.sin(A)
        cosB, sinB = math.cos(B), math.sin(B)
        for theta in [i * 0.3 for i in range(0, 21)]:
            costheta, sintheta = math.cos(theta), math.sin(theta)
            for phi in [i * 0.07 for i in range(0, 91)]:
                cosphi, sinphi = math.cos(phi), math.sin(phi)
                circlex = R2 * cosphi + R1
                circley = R2 * sinphi
                x = circlex * (cosB * costheta + sinA * sinB * sintheta) - circley * cosA * sinB
                y = circlex * (sinB * costheta - sinA * cosB * sintheta) + circley * cosA * cosB
                z = K2 + cosA * circlex * sintheta + circley * sinA
                ooz = 1 / z
                xp = int(width/2 + 2 * x * ooz * width/8)
                yp = int(height/2 + y * ooz * height/8)
                if 0 <= xp < width and 0 <= yp < height:
                    if ooz > zbuffer[yp][xp]:
                        zbuffer[yp][xp] = ooz
                        luminance = (costheta * cosphi * sinB - cosA * costheta * sinphi - sinA * sintheta + cosB * (cosA * sintheta - costheta * sinA * sinphi))
                        luminance_index = int(max(0,min(11,luminance*8)))
                        chars = ".,-~:;=!*#$@"
                        output[yp][xp] = chars[luminance_index]
        A += 0.07
        B += 0.03
        yield "\n".join("".join(row) for row in output)

def animated_intro():
    console.clear()
    # Space donut animation for 5 seconds
    with Live(console=console, refresh_per_second=15) as live:
        frames = donut_frames()
        start = time.time()
        while time.time() - start < 5:
            live.update(Panel(next(frames), title="Spinning Donut ✨", border_style="bright_magenta"))
    console.clear()

    console.print(Panel.fit(
        "[bold magenta]✨ Welcome to the world of Usman Ghani ✨[/bold magenta]",
        border_style="magenta"
    ))
    sleep(1)
    console.print(Panel.fit(
        "🚀 Machine Learning Developer\n🎯 Automation Engineer\n🧠 Python Powerhouse",
        title="[bold green]Who Am I[/bold green]",
        style="bold green"
    ))
    sleep(1)
    console.print("[cyan]🔗 GitHub:[/cyan] https://github.com/iamusmanbro")
    console.print("[cyan]🔗 LinkedIn:[/cyan] https://linkedin.com/in/iamusmanbro")
    sleep(0.5)
    console.print()
    console.print("[bold yellow]👉 Check out [bold]usman-ghani[/bold] on PyPI for real tools and code![/bold yellow]")
    console.print("[dim]💡 Thanks for installing![/dim]")

if __name__ == "__main__":
    animated_intro()
