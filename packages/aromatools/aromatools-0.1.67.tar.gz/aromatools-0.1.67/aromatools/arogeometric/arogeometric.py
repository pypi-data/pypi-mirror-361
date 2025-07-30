#!/usr/bin/python3
# -*- coding: utf-8 -*-

import math
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from ase.data import covalent_radii, atomic_numbers, chemical_symbols

# Diccionarios de parámetros
R_opt = {'HOMA93': {'CC': 1.388, 'CN': 1.334, 'NN': 1.309, 'CO': 1.265},
         'HOMER': {'CC': 1.437, 'CN': 1.39, 'NN': 1.375, 'CO': 1.379},
         'HOMAC': {'CC': 1.392, 'CN': 1.333, 'NN': 1.318, 'CO': 1.315, 'SiSi': 2.163, 'CSi': 1.752}}

alpha = {'HOMA93': {'CC': 257.7, 'CN': 93.52, 'NN': 130.33, 'CO': 157.38},
         'HOMER': {'CC': 950.74, 'CN': 506.43, 'NN': 187.36, 'CO': 164.96},
         'HOMAC': {'CC': 153.37, 'CN': 111.83, 'NN': 98.99, 'CO': 335.16, 'SiSi': 325.6, 'CSi': 115.41}}

def parse_xyz(file_xyz):
    with open(file_xyz, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    natoms = int(lines[0])
    atoms = []
    for i in range(2, 2 + natoms):
        parts = lines[i].split()
        if len(parts) < 4:
            continue
        symbol = parts[0].capitalize()
        if symbol == 'H':
            continue
        try:
            x, y, z = map(float, parts[1:4])
            atoms.append((symbol, x, y, z))
        except ValueError:
            raise ValueError(f"Invalid coordinates at line {i+1} in file {file_xyz}.")
    return atoms

def build_graph(atoms, tol=0.45):
    G = nx.Graph()
    for idx, (sym, _, _, _) in enumerate(atoms):
        G.add_node(idx, element=sym)
    for i in range(len(atoms)):
        sym1, x1, y1, z1 = atoms[i]
        r1 = covalent_radii[atomic_numbers[sym1]]
        for j in range(i + 1, len(atoms)):
            sym2, x2, y2, z2 = atoms[j]
            r2 = covalent_radii[atomic_numbers[sym2]]
            dist = math.sqrt((x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2)
            if dist <= r1 + r2 + tol:
                bond_type = ''.join(sorted(sym1 + sym2))
                G.add_edge(i, j, length=dist, bond_type=bond_type)
    return G

def find_rings_by_size(G, sizes=(5, 6)):
    from itertools import combinations
    rings = set()

    def dfs(path, depth):
        current = path[-1]
        if len(set(path)) != len(path):
            return

        if depth > max(sizes):
            return

        for neighbor in G.neighbors(current):
            if neighbor == path[0] and len(path) in sizes:
                cycle = path + [path[0]]
                if all(G.has_edge(cycle[i], cycle[i + 1]) for i in range(len(path))):
                    rings.add(tuple(sorted(path)))
            elif neighbor not in path:
                dfs(path + [neighbor], depth + 1)

    for start in G.nodes():
        dfs([start], 1)

    unique_rings = set()
    for ring in rings:
        ring = list(ring)
        min_idx = ring.index(min(ring))
        rotated = ring[min_idx:] + ring[:min_idx]
        unique_rings.add(tuple(rotated))

    return [list(r) for r in unique_rings]

def compute_index(G, atoms, index_type, filename=""):
    index_type = index_type.upper()

    if index_type not in ("HOMA", "HOMER"):
        raise ValueError("Invalid index. Use 'HOMA' o 'HOMER'.")

    rings = find_rings_by_size(G, sizes=(5, 6))
    ring_data = []

    for idx, ring in enumerate(rings, start=1):
        ring_atoms = ring + [ring[0]]
        distances = []
        bond_info = []

        for i in range(len(ring)):
            a1, a2 = ring_atoms[i], ring_atoms[i+1]
            sym1, x1, y1, z1 = atoms[a1]
            sym2, x2, y2, z2 = atoms[a2]
            dist = math.sqrt((x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2)
            distances.append(dist)

            bond_type = ''.join(sorted(sym1 + sym2))
            bond_data = {"type": bond_type, "length": dist}
            bond_info.append(bond_data)

        ring_data.append({
            "idx": idx,
            "distances": distances,
            "bonds": bond_info
        })

    results = []
    for ring in ring_data:
        idx = ring["idx"]
        bonds = ring["bonds"]
        distances = ring["distances"]
        row = {"Ring": f"Ring {idx}", "Bonds": [round(b["length"], 4) for b in bonds]}

        # BLA
        n = len(distances)
        bla = sum(abs(distances[i] - distances[(i+1) % n]) for i in range(n)) / n
        row["BLA"] = round(bla, 4)

        # HOMA93 / HOMAc / HOMER (según index_type)
        if index_type == "HOMA":
            for sub_index in ("HOMA93", "HOMAc"):
                valid = []
                for b in bonds:
                    bt = b["type"]
                    if bt in R_opt[sub_index]:
                        Ropt = R_opt[sub_index][bt]
                        a = alpha[sub_index][bt]
                        valid.append(a * (b["length"] - Ropt)**2)
                if valid:
                    n_valid = len(valid)
                    row[sub_index] = round(1.0 - sum(valid)/n_valid, 4)
        elif index_type == "HOMER":
            valid = []
            for b in bonds:
                bt = b["type"]
                if bt in R_opt["HOMER"]:
                    Ropt = R_opt["HOMER"][bt]
                    a = alpha["HOMER"][bt]
                    valid.append(a * (b["length"] - Ropt)**2)
            if valid:
                n_valid = len(valid)
                row["HOMER"] = round(1.0 - sum(valid)/n_valid, 4)

        results.append(row)

    df = pd.DataFrame(results)
    return rings, [(r["idx"], None) for r in ring_data], df

def draw_molecular_graph(G, atoms, rings, project_name, ring_indices):
    index_lookup = dict(ring_indices)
    pos = {}
    for idx, (_, x, y, z) in enumerate(atoms):
        pos[idx] = (x, y)
    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=False, node_size=300, node_color='lightblue', edge_color='gray')
    labels = {i: atoms[i][0] for i in range(len(atoms))}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)
    for i, ring in enumerate(rings, start=1):
        x_coords = [pos[a][0] for a in ring]
        y_coords = [pos[a][1] for a in ring]
        centroid = (sum(x_coords) / len(ring), sum(y_coords) / len(ring))
        index_value = index_lookup.get(i, None)
        if index_value is not None:
            label = f"{index_value:.3f}"
            plt.text(centroid[0], centroid[1], label, fontsize=10, fontweight='bold', color='red')
    plt.close()

def get_3Dgraph(G, atoms, rings, ring_indices, title="Molecular Graph 3D"):
    node_xyz = [(x, y, z) for _, x, y, z in atoms]
    edges = list(G.edges())
    x_edges = []
    y_edges = []
    z_edges = []
    for u, v in edges:
        x_edges += [node_xyz[u][0], node_xyz[v][0], None]
        y_edges += [node_xyz[u][1], node_xyz[v][1], None]
        z_edges += [node_xyz[u][2], node_xyz[v][2], None]
    x_nodes = [coord[0] for coord in node_xyz]
    y_nodes = [coord[1] for coord in node_xyz]
    z_nodes = [coord[2] for coord in node_xyz]
    symbols = [atoms[i][0] for i in range(len(atoms))]
    node_trace = go.Scatter3d(
        x=x_nodes, y=y_nodes, z=z_nodes,
        mode='markers+text',
        text=symbols,
        textposition='top center',
        marker=dict(size=5, color='lightblue'),
        name="Atoms"
    )
    edge_trace = go.Scatter3d(
        x=x_edges, y=y_edges, z=z_edges,
        mode='lines',
        line=dict(width=2, color='gray'),
        name="Bonds"
    )
    x_c_list, y_c_list, z_c_list, text_list = [], [], [], []
    for i, ring in enumerate(rings, start=1):
        coords = [node_xyz[a] for a in ring]
        x_c = sum(coord[0] for coord in coords) / len(coords)
        y_c = sum(coord[1] for coord in coords) / len(coords)
        z_c = sum(coord[2] for coord in coords) / len(coords)
        value = ring_indices.get(i, None) if isinstance(ring_indices, dict) else dict(ring_indices).get(i, None)
        if value is not None:
            x_c_list.append(x_c); y_c_list.append(y_c); z_c_list.append(z_c)
            text_list.append(f"{value:.3f}")
    centroid_trace = go.Scatter3d(
        x=x_c_list, y=y_c_list, z=z_c_list,
        mode='text',
        text=text_list,
        textfont=dict(size=10, color='red'),
        textposition='middle center',
        name="Indices"
    )
    fig = go.Figure(data=[edge_trace, node_trace, centroid_trace])
    fig.update_layout(
        title=title,
        margin=dict(l=0, r=0, b=0, t=30),
        showlegend=False,
        scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False))
    )
    return fig

def atoms_from_ase(ase_atoms):
    data = [(atom.symbol, *atom.position) for atom in ase_atoms]
    df = pd.DataFrame(data, columns=["Element", "X", "Y", "Z"])
    return df

def extract_atoms_from_output(fileout):
    atoms = []
    with open(fileout, 'r') as f:
        lines = f.readlines()
    if any("Entering Gaussian System" in line for line in lines):
        for i in range(len(lines) - 5):
            if "Standard orientation" in lines[i]:
                atoms = []
                j = i + 5
                while not "---" in lines[j]:
                    parts = lines[j].split()
                    atomic_number = int(parts[1])
                    symbol = chemical_symbols[atomic_number]
                    x, y, z = map(float, parts[3:6])
                    atoms.append((symbol, x, y, z))
                    j += 1
    elif any("O   R   C   A" in line for line in lines):
        atoms = []
        start = False
        for line in lines:
            if "CARTESIAN COORDINATES (ANGSTROEM)" in line:
                atoms = []
                start = True
                continue
            if start:
                if "---" in line or not line.strip():
                    start = False
                    continue
                parts = line.strip().split()
                if len(parts) == 4:
                    symbol = parts[0]
                    x, y, z = map(float, parts[1:])
                    atoms.append((symbol, x, y, z))
    df = pd.DataFrame(atoms, columns=["Element", "X", "Y", "Z"])
    return df
