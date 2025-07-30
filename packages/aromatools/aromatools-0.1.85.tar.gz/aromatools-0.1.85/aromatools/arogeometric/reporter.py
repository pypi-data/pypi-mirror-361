import pandas as pd
from aromatools.arogeometric.arogeometric import build_graph, compute_index, get_3Dgraph

class AtomsReporter:
    def __init__(self, mol, index_type: str):
        self.index_type = index_type.upper()
        atoms_list = []
        for atom in mol:
            symbol = atom.symbol.capitalize()
            if symbol == 'H':
                continue
            x, y, z = atom.position
            atoms_list.append((symbol, x, y, z))

        self._graph = build_graph(atoms_list)

        # Ahora compute_index devuelve dos DataFrames
        rings, ring_indices_list, df_index, df_bonds = compute_index(
            self._graph, atoms_list, self.index_type
        )

        # Selección de columnas según tipo de índice
        if self.index_type == "HOMA":
            self._df_main = df_index[["Ring", "HOMA93", "HOMAC", "BLA"]]
        elif self.index_type == "HOMER":
            self._df_main = df_index[["Ring", "HOMER", "BLA"]]
        else:
            self._df_main = df_index  # fallback, en caso de error

        self._df_bonds = df_bonds
        ring_idx_dict = dict(ring_indices_list)

        self._fig = get_3Dgraph(self._graph, atoms_list, rings, ring_idx_dict)

    def df_main(self) -> pd.DataFrame:
        """Índices por anillo: HOMA93, HOMAC, HOMER, BLA"""
        return self._df_main

    def df_bonds(self) -> pd.DataFrame:
        """Distancias de enlace por anillo."""
        return self._df_bonds

    def fig(self):
        """Figura interactiva 3D del grafo."""
        return self._fig
