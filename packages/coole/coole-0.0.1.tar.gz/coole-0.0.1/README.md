# coole

A Python tool to get Google autosuggest keywords with recursive search and a rich terminal UI.

## Installation

Install `coole` using pip:

```bash
pip install coole
```

Alternatively, you can install it from the source:

```bash
git clone https://github.com/your-username/coole.git
cd coole
pip install .
```

## Usage

```bash
coole <query> [options]
```

### Parameters

*   `query`: The initial search query (required).
*   `-d`, `--depth`: The depth of the recursive search (optional, default: 1).

### Examples

#### Basic Usage

To get suggestions for the query "python":

```bash
coole python
```

#### Recursive Search

To perform a recursive search with a depth of 2 for the query "python":

```bash
coole python -d 2
```

## How it works

`coole` fetches suggestions from Google's autosuggest API. It can perform a recursive search, where it takes the suggestions from the initial query and uses them as new queries to find more suggestions. The results are displayed in a clean and readable table in your terminal.