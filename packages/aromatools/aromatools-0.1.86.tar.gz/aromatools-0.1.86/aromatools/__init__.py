# __init__.py de AROMATOOLS
# Este archivo define qué clases y funciones se pueden importar directamente desde el paquete:
# Ejemplo de uso:
#   from aromatools import *  # Importa todas las funciones listadas en __all__

# AroGeometric module
from .arogeometric.reporter import AtomsReporter
from .arogeometric.arogeometric import build_graph, compute_index, get_3Dgraph

# AroMagnetic module (ejemplo)
# from .aromagnetic.magnetic_utils import compute_nics, plot_current_map

# Lista de símbolos que se exportan al hacer: from aromatools import *
__all__ = [
    "AtomsReporter",
    "build_graph",
    "compute_index",
    "get_3Dgraph",
    # "compute_nics",         # ← Descomenta cuando lo implementes
    # "plot_current_map"
]

