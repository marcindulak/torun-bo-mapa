[![test](https://github.com/marcindulak/torun-bo-mapa/actions/workflows/test.yml/badge.svg)](https://github.com/marcindulak/torun-bo-mapa/actions/workflows/test.yml)

> Co-Authored-By: Claude

# Functionality overview

Map visualization of the voting results of budżet obywatelski of the city of Toruń, Poland.

# Usage examples

The instructions below describe how to add a new budget year to `index.html`.

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)

2. Clone this repository:

   ```
   git clone https://github.com/marcindulak/torun-bo-mapa
   cd torun-bo-mapa
   ```

3. Install Python dependencies:

   ```
   uv sync --frozen
   ```

4. Extract budget data from PDF:

   ```
   uv run --frozen python preprocessing/extract_bo_2025.py > bo/2025.raw.json
   ```

5. Manually add `address` and `category` to the generated JSON file for all entries, and save the file as `bo/2025.json`.
You need to use a human judgment to determine the `address`, sometimes looking for it in other documents present on https://torun.pl/pl/bo or https://bip.torun.pl/artykuly/32484/budzet-torunia.
You'll find the `category` id assignment for each project in the "Plan budżetu" document available at https://bip.torun.pl/artykuly/32484/budzet-torunia, in the `Dział` column.

6. Perform geolocation:

   ```
   uv run --frozen python preprocessing/perform_geolocation.py bo/2025.json
   ```

7. Include the contents of `bo/2025.json` into the `index.html` file.

# Running tests

## Integration test

End-to-end test verifies the overall functionality of the preprocessing steps:

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
The PDF files downloaded manually from https://torun.pl/pl/bo are saved under the `bo` folder, and cleaned using Python scripts located in the `preprocessing` folder.
The outcome of the preprocessing steps is a file in JSON format, that is embedded verbatim in the `index.html` file for CORS compatibility.
The visualization uses Leaflet to place budget markers on an OpenStreetMap.

Addresses are manually filled in the address field of each entry in the JSON file to ensure accurate geocoding.

The following information was used for manual entry:
- 2025: `address` (https://torun.pl/pl/budzet-obywatelski-2025-ostateczna-lista-projektow-do-glosowania), `category` (https://prawomiejscowe.pl/UrzadMiastaTorunia/document/1132802/Uchwala-146_24 Zalacznik29.pdf)

# Abandoned ideas

- Loading data from separate JSON files: discarded due to CORS restrictions when opening HTML files directly in browsers.
- Using a web server to serve the application: discarded to avoid hosting requirements.
- Using regex patterns or spaCy for address parsing: only human address verification is reliable.
