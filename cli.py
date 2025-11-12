# cli.py
import typer

app = typer.Typer()

@app.command()
def greet(name: str):
    """Say hello to someone."""
    typer.echo(f"Hello {name}!")

if __name__ == "__main__":
    app()

