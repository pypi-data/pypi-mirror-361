import requests
import json
import argparse
from rich.console import Console
from rich.table import Table

def get_suggestions(query):
    """Fetches suggestions for a given query."""
    try:
        url = f"https://www.google.com/complete/search?q={query}&client=gws-wiz&xssi=t"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = json.loads(response.text[5:])
        return [item[0].replace("<b>", "").replace("</b>", "") for item in data[0]]
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error fetching suggestions for '{query}': {e}[/bold red]")
        return []
    except (json.JSONDecodeError, IndexError):
        console.print(f"[bold yellow]Could not parse suggestions for '{query}'.[/bold yellow]")
        return []

def recursive_search(query, depth, console):
    """Recursively searches for suggestions."""
    if depth == 0:
        return

    table = Table(title=f"Suggestions for '{query}' (Depth: {depth})")
    table.add_column("Suggestion", style="cyan")

    suggestions = get_suggestions(query)
    for suggestion in suggestions:
        table.add_row(suggestion)

    console.print(table)

    for suggestion in suggestions:
        recursive_search(suggestion, depth - 1, console)

def main():
    """Main function to run the tool."""
    parser = argparse.ArgumentParser(description="Get Google autosuggest keywords with recursive search.")
    parser.add_argument("query", help="The initial search query.")
    parser.add_argument("-d", "--depth", type=int, default=1, help="The depth of the recursive search.")
    args = parser.parse_args()

    console = Console()
    recursive_search(args.query, args.depth, console)

if __name__ == "__main__":
    main()