from rich import print
from rich.console import Console
from rich.panel import Panel
from time import sleep

console = Console()

def animated_intro():
    console.clear()
    console.print("[bold magenta]
✨ Welcome to the world of Usman Ghani ✨[/bold magenta]")
    sleep(1)
    console.print(Panel.fit("🚀 Machine Learning Developer
🎯 Automation Engineer
🧠 Python Powerhouse", title="Who Am I", style="bold green"))
    sleep(1)
    console.print("[cyan]GitHub:[/cyan] https://github.com/iamusmanbro")
    console.print("[cyan]LinkedIn:[/cyan] https://linkedin.com/in/iamusmanbro")
    console.print("[cyan]YouTube:[/cyan] https://youtube.com/@iamusmanbro")
    console.print("
[bold yellow]👉 Check out [usman-ghani] on PyPI for real tools and code[/bold yellow]")
    console.print("[dim]Thanks for installing![/dim]")

if __name__ == "__main__":
    animated_intro()
