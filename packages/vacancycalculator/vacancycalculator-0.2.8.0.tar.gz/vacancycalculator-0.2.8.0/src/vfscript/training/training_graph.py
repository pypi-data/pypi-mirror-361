import os
import json
import copy
import numpy as np
import networkx as nx
from scipy.spatial import ConvexHull
from ovito.io import import_file, export_file
from ovito.modifiers import (
    ExpressionSelectionModifier,
    DeleteSelectedModifier,
    ConstructSurfaceModifier
)
from vfscript.training.utils import resolve_input_params_path

class AtomicGraphGenerator:
    def __init__(self, json_params_path: str = None):
        if json_params_path is None:
            json_params_path = resolve_input_params_path("input_params.json")
        with open(json_params_path, "r", encoding="utf-8") as f:
            all_params = json.load(f)
        cfg = all_params["CONFIG"][0]
        self.input_path = cfg['relax']
        self.cutoff = cfg['cutoff']
        self.radius = cfg['radius']
        self.smoothing_level_training = cfg['smoothing_level_training']
        self.num_iterations = cfg['max_graph_variations']
        self.max_nodes = cfg['max_graph_size']
        self.pipeline = import_file(self.input_path, multiple_frames=True)
        self.metrics = {
            'surface_area': [],
            'filled_volume': [],
            'vacancies': [],
            'cluster_size': []
        }
        # Asegurarse de que existan las carpetas de salida
        os.makedirs('outputs/json', exist_ok=True)
        os.makedirs('outputs/dump', exist_ok=True)

    def run(self):
        for iteration in range(1, self.num_iterations + 1):
            for length in range(6, self.max_nodes + 1):
                ids, coords = self._generate_graph(length)
                expr = " || ".join(f"ParticleIdentifier=={pid}" for pid in ids)
                area, volume, count = self._export_graph(expr, iteration, length)
                self.metrics['surface_area'].append(area)
                self.metrics['filled_volume'].append(volume)
                self.metrics['vacancies'].append(len(ids))
                self.metrics['cluster_size'].append(count)
        # Exportar métricas finales
        with open('outputs/json/training_graph.json', 'w') as f:
            json.dump(self.metrics, f, indent=4)
        print('Exported metrics to outputs/json/training_graph.json')

    def _generate_graph(self, length: int):
        data = self.pipeline.compute()
        pos = data.particles.positions.array
        ids_arr = data.particles['Particle Identifier'].array
        N = len(pos)
        start = np.random.choice(N)
        coords = [pos[start]]
        ids = [int(ids_arr[start])]
        current = coords[0]
        remaining = set(range(N))
        remaining.remove(start)
        while len(coords) < length and remaining:
            rem = np.array(list(remaining))
            dists = np.linalg.norm(pos[rem] - current, axis=1)
            order = np.argsort(dists)
            top2 = order[:2] if len(order) >= 2 else order
            choice = np.random.choice(rem[top2])
            coords.append(pos[choice])
            ids.append(int(ids_arr[choice]))
            current = pos[choice]
            remaining.remove(choice)
        return ids, coords

    def _export_graph(self, expr: str, iteration: int, length: int):
        # Clonar pipeline y aplicar selección
        p = copy.deepcopy(self.pipeline)
        p.modifiers.append(ExpressionSelectionModifier(expression=expr))
        p.modifiers.append(DeleteSelectedModifier())
        p.modifiers.append(ConstructSurfaceModifier(
            radius=self.radius,
            smoothing_level=self.smoothing_level_training,
            select_surface_particles=True
        ))
        data = p.compute()
        points = data.particles.positions.array
        count = len(points)
        if count >= 4:
            hull = ConvexHull(points)
            area = hull.area
            volume = hull.volume
        else:
            area = 0.0
            volume = 0.0
        # Exportar dump con nombre único por iteración y longitud
        filename = f'outputs/dump/graph_it{iteration:02d}_len{length:03d}_cnt{count:02d}.dump'
        export_file(
            p,
            filename,
            'lammps/dump',
            columns=[
                'Particle Identifier','Particle Type',
                'Position.X','Position.Y','Position.Z'
            ]
        )
        p.modifiers.clear()
        return area, volume, count

if __name__ == '__main__':
    generator = AtomicGraphGenerator()
    generator.run()
