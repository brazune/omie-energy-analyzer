# omie-energy-analyzer
Tool to retrieve and analyze OMIE files for energy prices in Portugal

```
usage: omie-energy-analyzer.py [-h] [--initialize-history] [--get-day GET_DAY] [--get-tomorrow] [--analyze] [--dir DIR] [--file FILE] [--graph]

Parameterized functions example

optional arguments:
  -h, --help            show this help message and exit
  --initialize-history  Retrieve OMIE price history for current year
  --get-day GET_DAY     Retrieve the OMIE price file with a timestamp parameter (YYYY-MM-DD)
  --get-tomorrow        Get OMIE price file for tomorrow
  --analyze             Performs an analysis on the price files
  --dir DIR             Directory containing CSV files. Used only if --analyze is specified.
  --file FILE           File extension of CSV files Used only if --analyze is specified.
  --graph               Display a graph with the price analysis Used only if --analyze is specified.
```
