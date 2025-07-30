import json
import copy
import numpy as np
from scipy.spatial import ConvexHull, cKDTree
from ovito.io import import_file, export_file
from ovito.modifiers import (
    ExpressionSelectionModifier,
    DeleteSelectedModifier,
    ClusterAnalysisModifier,
    ConstructSurfaceModifier,
    InvertSelectionModifier
)

from vfscript.training.utils import resolve_input_params_path

class AtomicGraphGeneratorA:
    def __init__(self,
                 json_params_path: str = None,
                 num_iterations: int = 100,
                 max_nodes: int = 4,
                 k_neighbors: int = 3):
        """
        Generador de grafos atómicos mejorado: tras elegir el átomo inicial,
        selecciona aleatoriamente entre los k vecinos más cercanos.

        :param json_params_path: Ruta al JSON de parámetros de entrada.
        :param num_iterations: Número de iteraciones de muestreo.
        :param max_nodes: Longitud máxima del camino atómico.
        :param k_neighbors: Número de vecinos más cercanos a considerar para elección aleatoria.
        """
        if json_params_path is None:
            json_params_path = resolve_input_params_path("input_params.json")

        with open(json_params_path, "r", encoding="utf-8") as f:
            all_params = json.load(f)
        if "CONFIG" not in all_params or not isinstance(all_params["CONFIG"], list) or len(all_params["CONFIG"]) == 0:
            raise KeyError("input_params.json debe contener la clave 'CONFIG' como lista no vacía.")
        cfg = all_params["CONFIG"][0]
        self.input_path = cfg['relax']
        self.cutoff = cfg['cutoff']
        self.radius = cfg['radius']
        self.smoothing_level_training = cfg['smoothing_level_training']

        self.num_iterations = num_iterations
        self.max_nodes = max_nodes
        self.k_neighbors = max(1, k_neighbors)

        self.pipeline = import_file(self.input_path, multiple_frames=True)
        self.metrics = {
            'surface_area': [],
            'filled_volume': [],
            'vacancys': [],
            'cluster_size': []
        }

    def run(self):
        for iteration in range(1, self.num_iterations + 1):
            for length in range(1, self.max_nodes + 1):
                ids, coords = self._generate_graph(length)
                expr = " || ".join(f"ParticleIdentifier=={pid}" for pid in ids)
                area, volume, count = self._export_graph(expr)
                self.metrics['surface_area'].append(area)
                self.metrics['filled_volume'].append(volume)
                self.metrics['vacancys'].append(len(ids))
                self.metrics['cluster_size'].append(count)
        with open('outputs/json/training_graph_A.json', 'w') as f:
            json.dump(self.metrics, f, indent=4)
        print('Exported metrics to training_graph_A.json')

    def _generate_graph(self, length: int):
        data = self.pipeline.compute()
        pos = data.particles.positions.array
        ids_arr = data.particles['Particle Identifier'].array
        N = len(pos)

        # Construir árbol KD para búsqueda rápida
        tree = cKDTree(pos)

        # Elegir átomo inicial aleatoriamente
        start_idx = np.random.randint(N)
        coords = [pos[start_idx]]
        ids = [int(ids_arr[start_idx])]

        remaining = set(range(N))
        remaining.remove(start_idx)
        current_idx = start_idx

        while len(coords) < length and remaining:
            # Consultar k vecinos más cercanos del átomo actual
            dists, neighbors = tree.query(pos[current_idx], k=self.k_neighbors + 1)
            # tree.query incluye el propio índice como vecino 0
            candidates = [idx for idx in neighbors if idx in remaining]
            if not candidates:
                break
            # Elegir aleatoriamente entre los k vecinos más cercanos disponibles
            choice = np.random.choice(candidates)
            coords.append(pos[choice])
            ids.append(int(ids_arr[choice]))
            remaining.discard(choice)
            current_idx = choice

        return ids, coords

    def _export_graph(self, expr: str):
        p = copy.deepcopy(self.pipeline)
        p.modifiers.append(ExpressionSelectionModifier(expression=expr))
        p.modifiers.append(DeleteSelectedModifier())
        p.modifiers.append(ConstructSurfaceModifier(
            radius=self.radius,
            smoothing_level=self.smoothing_level_training,
            select_surface_particles=True
        ))
        p.modifiers.append(InvertSelectionModifier())
        p.modifiers.append(DeleteSelectedModifier())
        p.modifiers.append(ClusterAnalysisModifier(cutoff=self.cutoff, unwrap_particles=True))

        data = p.compute()
        points = data.particles.positions.array
        count = len(points)
        if count >= 4:
            hull = ConvexHull(points)
            area = hull.area
            volume = hull.volume
        else:
            area, volume = 0.0, 0.0

        export_file(
            p,
            f'outputs/dump/graph_A_{count}.dump',
            'lammps/dump',
            columns=[
                'Particle Identifier', 'Particle Type',
                'Position.X', 'Position.Y', 'Position.Z'
            ]
        )
        p.modifiers.clear()
        return area, volume, count

if __name__ == '__main__':
    generator = AtomicGraphGeneratorA(k_neighbors=6)
    generator.run()
