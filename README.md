[![test](https://github.com/marcindulak/torun-bo-mapa/actions/workflows/test.yml/badge.svg)](https://github.com/marcindulak/torun-bo-mapa/actions/workflows/test.yml)

> Co-Authored-By: Claude

> [!NOTE]
> The project is not affiliated with Toruń Municipal Office ("Projekt niezwiązany z Urzędem Miasta Torunia")

# Functionality overview

Map visualization of the budżet obywatelski of the city of Toruń, Poland, with an interactive game mode to test knowledge about city projects.

Available at [https://marcindulak.github.io/torun-bo-mapa](https://marcindulak.github.io/torun-bo-mapa).

## Map Mode

View all accepted and rejected citizen budget projects on an interactive map. Click on markers to view project details.

## Game Mode

Test your knowledge of the citizen budget projects. Click "Sprawdź Swoją Wiedzę!" to start a game with 5 randomly selected projects.

In each game round, you answer two questions:
1. **Identify the project**: Given a project category, identify the correct project name from 2 choices (closest projects in the same category, supplemented from other categories if needed).
2. **Guess the budget range**: Estimate whether the project costs less than 100,000 zł, between 100,000-500,000 zł, or more than 500,000 zł.

Each correct answer earns 1 point (max 10 points per game). After answering each question, the correct answer and project details are displayed for 8 seconds, or may be skipped by pressing "Następny" button.
After 5 projects, your final score is shown with confetti animation.

You can exit the game at any time by pressing ESC.

# Usage examples

## Adding a New Budget Year

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
   uv run --frozen python preprocessing/extract_bo_2025.py > data/2025.raw.json
   ```

5. `cp -f data/2025.raw.json data/2025.json` and manually add `address` and `category` to the `data/2025.json` file for all entries.
You need to use a human judgment to determine the `address`, sometimes looking for it in other documents present on https://torun.pl/pl/bo or https://bip.torun.pl/artykuly/32484/budzet-torunia.
You'll find the `category` id assignment for each project in the "Plan budżetu" document available at https://bip.torun.pl/artykuly/32484/budzet-torunia, in the `Dział` column.

6. Perform geolocation:

   ```
   uv run --frozen python preprocessing/perform_geolocation.py data/2025.json
   ```

7. Include the contents of `data/2025.json` into the `index.html` file.

# Running tests

## Type checking

Run mypy static type checking:

```
uv run --frozen python -m mypy preprocessing
```

# Implementation overview

The frontend is a static HTML application with embedded JavaScript using ES modules, hosted on Github Pages.
The PDF files downloaded manually from https://torun.pl/pl/bo are saved under the `bo` folder, and cleaned using Python scripts located in the `preprocessing` folder.
The outcome of the preprocessing steps is a file in JSON format, that is embedded verbatim in the `index.html` file for CORS compatibility.
The visualization uses Leaflet to place budget markers on an OpenStreetMap.

Addresses are manually filled in the address field of each entry in the JSON file to ensure accurate geocoding.

The following information was used for manual entry:
- 2026: `address` (https://torun.pl/pl/budzet-obywatelski-2026-ostateczna-lista-projektow-do-glosowania), `category` (TODO)
- 2025: `address` (https://torun.pl/pl/budzet-obywatelski-2025-ostateczna-lista-projektow-do-glosowania), `category` (https://prawomiejscowe.pl/UrzadMiastaTorunia/document/1132802/Uchwala-146_24 Zalacznik29.pdf)
- 2024: `address` (https://torun.pl/pl/budzet-obywatelski-w-toruniu-2024), `category` (https://prawomiejscowe.pl/UrzadMiastaTorunia/document/1009669/Uchwala-1237_23 Zalacznik30.pdf)

Suggestions for data owners:
1. Keep the "Nazwa projektu", "Lokalizacja", "Opis" in separate columns.
2. Provide standardized "Lokalizacja", ideally with geolocation data.
3. If multiple localizations are covered by the project, provide them as entries in a separate column. Do not use free form text like "Ulica A, oraz czesc ulicy B" or similar, since they are hard to parse by a machine.

# Abandoned ideas

- Loading data from separate JSON files: discarded due to CORS restrictions when opening HTML files directly in browsers.
- Using a web server to serve the application: discarded to avoid hosting requirements.
- Using regex patterns or spaCy for address parsing: only human address verification is reliable.
