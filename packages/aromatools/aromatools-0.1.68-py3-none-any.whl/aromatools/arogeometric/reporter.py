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
        rings, ring_indices_list, df_index = compute_index(self._graph, atoms_list, self.index_type)

        self._df = df_index

        # Selección del índice visual por defecto
        if self.index_type == "HOMA" and "HOMAC" in df_index.columns:
            ring_idx_dict = dict(zip(df_index["Ring"], df_index["HOMAC"]))
        elif self.index_type == "HOMER" and "HOMER" in df_index.columns:
            ring_idx_dict = dict(zip(df_index["Ring"], df_index["HOMER"]))
        else:
            print("[!] No se encontró un índice estándar para visualización. Se usará BLA.")
            ring_idx_dict = dict(zip(df_index["Ring"], df_index["BLA"]))

        self._fig = get_3Dgraph(self._graph, atoms_list, rings, ring_idx_dict)

    def df(self) -> pd.DataFrame:
        return self._df

    def fig(self):
        return self._fig
