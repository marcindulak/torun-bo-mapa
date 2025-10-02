[![test](https://github.com/marcindulak/torun-budzet-wizualizacja/actions/workflows/test.yml/badge.svg)](https://github.com/marcindulak/torun-budzet-wizualizacja/actions/workflows/test.yml)

> Co-Authored-By: Claude

# Functionality overview

Visualization of the budget of the city of Toruń, Poland.

# Usage examples

The full setup instructions follow below.

1. Install [Docker Engine](https://docs.docker.com/engine/install/) or [Docker Desktop](https://docs.docker.com/desktop/)

2. Install [Docker Compose](https://docs.docker.com/compose/install/)

3. Clone this repository, and `cd` into it:

   ```
   git clone https://github.com/marcindulak/torun-budzet-wizualizacja
   cd torun-budzet-wizualizacja
   ```

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

# Abandoned ideas

- Loading data from separate JSON files: discarded due to CORS restrictions when opening HTML files directly in browsers.
- Using a web server to serve the application: discarded to avoid hosting requirements.
