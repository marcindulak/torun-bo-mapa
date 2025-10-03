[![test](https://github.com/marcindulak/torun-budzet-wizualizacja/actions/workflows/test.yml/badge.svg)](https://github.com/marcindulak/torun-budzet-wizualizacja/actions/workflows/test.yml)

> Co-Authored-By: Claude

# Functionality overview

Visualization of the budget of the city of Toruń, Poland.

# Usage examples

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)

2. Clone this repository:

   ```
   git clone https://github.com/marcindulak/torun-budzet-wizualizacja
   cd torun-budzet-wizualizacja
   ```

3. Fetch machine learning models (this needs to be performed only once):

   ```
   uv add --no-deps 'pl-core-news-sm @ https://github.com/explosion/spacy-models/releases/download/pl_core_news_sm-3.8.0/pl_core_news_sm-3.8.0-py3-none-any.whl'
   ```

4. Install Python dependencies:

   ```
   uv sync
   ```

5. Extract budget data from PDF:

   ```
   uv run python preprocessing/extract_budzet_obywatelski_2024.py > budzet_obywatelski_2024.json
   ```

6. Find entries that failed geocoding:

   ```
   uv run python preprocessing/find_failed_geocoding.py
   ```

   Copy output into `preprocessing/extract_budzet_obywatelski_2024.py` in `get_manual_address`, update addresses from `"Reja 1"` to actual locations.

7. Add successful geocoding to tests:

   ```
   uv run python preprocessing/find_failed_geocoding.py 2>&1 | grep -A 9999 "SUCCEEDED ENTRIES"
   ```

   Copy output into `preprocessing/extract_budzet_obywatelski_2024.py` in `test_known_good_locations`.

# Running tests

Tests run inside Docker containers to have access to required dependencies.

## Unit tests

```
bash scripts/test_unit.sh
```

## Integration test

End-to-end test verifies the overall functionality the the user perspective:

```
bash scripts/test_e2e.sh
```

## Type checking

Run mypy static type checking:

```
bash scripts/test_mypy.sh
```

# Implementation overview

The frontend is a static HTML application with embedded JavaScript using ES modules, hosted on Github Pages.
The data originates from https://bip.torun.pl/artykuly/32484/budzet-torunia, and is to be saved manually under the `noupload` folder.
The saved files are cleaned and curated using Python scripts located in the `preprocessing` folder.
The outcome of the preprocessing steps is a file in JSON format, that is embedded verbatim in the `index.html` file for CORS compatibility.
The visualization uses Leaflet to place budget markers on an OpenStreetMap.

Location parsing uses spaCy NER and pattern matching. Entries that fail geocoding can be manually overridden using the `get_manual_address` function. Successfully geocoded entries are automatically tested for regression using the `test_known_good_locations` function.

# Abandoned ideas

- Loading data from separate JSON files: discarded due to CORS restrictions when opening HTML files directly in browsers.
- Using a web server to serve the application: discarded to avoid hosting requirements.
- Using regex patterns for address parsing: discarded in favor of spaCy for better maintainability.
