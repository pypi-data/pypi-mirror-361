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

        if self.index_type == "HOMER":
            rings, ring_indices_list, df_index = compute_index(self._graph, atoms_list, "HOMER")
        elif self.index_type == "HOMA":
            rings93, _, df93 = compute_index(self._graph, atoms_list, "HOMA93")
            rings_c, _, df_c = compute_index(self._graph, atoms_list, "HOMAc")
            rings_bla, _, df_bla = compute_index(self._graph, atoms_list, "BLA")

            assert rings93 == rings_c == rings_bla
            rings = rings93
            ring_indices_list = list(enumerate([None]*len(rings), start=1))

            df_index = pd.concat([
                df93.set_index("Ring"),
                df_c.set_index("Ring")["HOMAc"],
                df_bla.set_index("Ring")["BLA"]
            ], axis=1).reset_index()
        else:
            rings, ring_indices_list, df_index = compute_index(self._graph, atoms_list, self.index_type)

        self._df = df_index

        if self.index_type == "HOMA":
            try:
                ring_idx_dict = dict(zip(df_index["Ring"], df_index["HOMAc"]))
            except KeyError:
                ring_idx_dict = dict(zip(df_index["Ring"], df_index["HOMA93"]))
        else:
            key = self.index_type
            if key == "HOMA":
                key = "HOMA93"
            ring_idx_dict = dict(zip(df_index["Ring"], df_index[key]))

        self._fig = get_3Dgraph(self._graph, atoms_list, rings, ring_idx_dict)

    def df(self) -> pd.DataFrame:
        return self._df

    def fig(self):
        return self._fig
