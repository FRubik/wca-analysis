"""Configuração central: caminhos, recortes de análise e parâmetros do mapa."""

from datetime import date
from pathlib import Path

# ----------------------------------------------------------------------
# Caminhos
# ----------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
TSV_DIR = BASE_DIR / "tsv"
OUTPUT_HTML = BASE_DIR / "index.html"

# ----------------------------------------------------------------------
# Análise de modalidades
# ----------------------------------------------------------------------
# Modalidades descontinuadas / fora de escopo
EXCLUDED_EVENTS = ["3x3x3 Multi-Blind Old Style", "Magic", "Master Magic"]

WORLD_START_YEAR = 2003
BRAZIL_START_YEAR = 2006
MAX_YEAR = date.today().year

# Recortes geográficos (cláusula WHERE aplicada às competições)
SCOPE_WORLD = ""
SCOPE_BRAZIL = "c.country_id = 'Brazil'"
SCOPE_SP = "c.country_id = 'Brazil' AND c.city_name LIKE '%, São Paulo'"

# ----------------------------------------------------------------------
# Mapa de cobertura
# ----------------------------------------------------------------------
RADIUS_OPTIONS_KM = [50, 100, 150, 200]        # raios oferecidos no seletor
DEFAULT_RADIUS_KM = 100                         # raio selecionado por padrão
COVERAGE_START_YEAR = 2022                      # menor ano oferecido no seletor
COVERAGE_DEFAULT_YEAR = 2024                    # recorte selecionado por padrão
COVERAGE_YEAR_OPTIONS = list(range(COVERAGE_START_YEAR, MAX_YEAR + 1))
GRID_STEP_DEG = 0.08                            # resolução da grade (~9 km)
EARTH_RADIUS_KM = 6371.0
