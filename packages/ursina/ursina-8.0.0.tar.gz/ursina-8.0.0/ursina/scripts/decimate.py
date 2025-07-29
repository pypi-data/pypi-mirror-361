import math

def decimate_mesh(vertices, triangles, target_ratio):
    """
    Simplifies a mesh to a target ratio of the original face count.
    
    Args:
        vertices (list of list): List of vertex positions [[x, y, z], ...].
        triangles (list of list): List of triangles [[v1, v2, v3], ...].
        target_ratio (float): Target ratio of remaining faces (0.0 to 1.0).
        
    Returns:
        tuple: Simplified vertices and triangles.
    """
    def edge_length(v1, v2):
        """Calculate the length of an edge."""
        return math.sqrt(
            (v1[0] - v2[0])**2 +
            (v1[1] - v2[1])**2 +
            (v1[2] - v2[2])**2
        )

    def midpoint(v1, v2):
        """Calculate the midpoint of two vertices."""
        return [(v1[0] + v2[0]) / 2, (v1[1] + v2[1]) / 2, (v1[2] + v2[2]) / 2]

    # Compute target number of triangles
    target_count = int(len(triangles) * target_ratio)

    # Build edge list with lengths
    edges = {}
    for tri in triangles:
        for i in range(3):
            edge = tuple(sorted((tri[i], tri[(i + 1) % 3])))
            if edge not in edges:
                edges[edge] = edge_length(vertices[edge[0]], vertices[edge[1]])

    # Sort edges by length
    sorted_edges = sorted(edges.items(), key=lambda x: x[1])

    # Start collapsing edges
    while len(triangles) > target_count and sorted_edges:
        edge, _ = sorted_edges.pop(0)
        v1, v2 = edge

        # Compute new vertex as midpoint
        new_vertex = midpoint(vertices[v1], vertices[v2])
        new_vertex_idx = len(vertices)
        vertices.append(new_vertex)

        # Update triangles to use the new vertex
        new_triangles = []
        for tri in triangles:
            if v1 in tri or v2 in tri:
                # Replace v1 and v2 with the new vertex index
                tri = [new_vertex_idx if v == v1 or v == v2 else v for v in tri]
                if len(set(tri)) == 3:  # Keep only valid triangles
                    new_triangles.append(tri)
            else:
                new_triangles.append(tri)
        triangles = new_triangles

        # Recompute edges and sort
        edges = {}
        for tri in triangles:
            for i in range(3):
                edge = tuple(sorted((tri[i], tri[(i + 1) % 3])))
                if edge not in edges:
                    edges[edge] = edge_length(vertices[edge[0]], vertices[edge[1]])
        sorted_edges = sorted(edges.items(), key=lambda x: x[1])

    return vertices, triangles


from ursina import Vec3
from copy import copy
import math
from ursina.scripts.cythonizer import cythonize_function

def cross(v1:Vec3, v2:Vec3) -> Vec3: 
    return (
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    )

def normalize(v:Vec3) -> Vec3:
    import math
    length = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    return (v[0] / length, v[1] / length, v[2] / length) if length > 0 else (0, 0, 0)

def dot(v1:Vec3, v2:Vec3):
    return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]

def compute_face_normal(vertices, tri) -> Vec3:
    """Compute normal for a single triangle."""
    v1:Vec3 = subtract(vertices[tri[1]], vertices[tri[0]])
    v2:Vec3 = subtract(vertices[tri[2]], vertices[tri[0]])
    return normalize(cross(v1, v2))

def compute_dihedral_angle(normal1:Vec3, normal2:Vec3):
    """Compute dihedral angle (in degrees) between two normals."""
    import math
    dot_product = dot(normal1, normal2)
    dot_product = max(-1.0, min(1.0, dot_product))  # Clamp to avoid errors
    angle_radians = math.acos(dot_product)
    return math.degrees(angle_radians)

def edge_to_triangles_map(triangles):
    """Build a mapping of edges to the triangles that share them."""
    edge_map = {}
    for i, tri in enumerate(triangles):
        for j in range(3):
            edge = tuple(sorted((tri[j], tri[(j + 1) % 3])))
            if edge not in edge_map:
                edge_map[edge] = []
            edge_map[edge].append(i)
    return edge_map

def subtract(v1:Vec3, v2:Vec3):
    result = Vec3(v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2])
    return result


from ursina.scripts import cythonizer

@cythonize_function(include=(subtract, cross, normalize, dot, compute_face_normal, compute_dihedral_angle, edge_to_triangles_map))
def decimate_mesh_by_angle(vertices, triangles, angle_threshold):
    compiled = 'compiled' if __file__.endswith('.so') else 'pure python'
    from time import perf_counter
    import random
    t = perf_counter()

    import math
    # Ensure all vertices are tuples
    # vertices = [tuple(v) for v in vertices]

    # Precompute normals
    normals = [compute_face_normal(vertices, tri) for tri in triangles]

    # Map edges to triangles
    edge_map = edge_to_triangles_map(triangles)

    # List of edges to collapse
    collapsible_edges = []

    for edge, tri_indices in edge_map.items():
        if len(tri_indices) == 2:  # Only consider edges shared by two triangles
            tri1, tri2 = tri_indices
            angle = compute_dihedral_angle(normals[tri1], normals[tri2])
            if angle <= angle_threshold:
                collapsible_edges.append(edge)

    # Perform edge collapses
    new_vertices = list(vertices)
    new_triangles = list(triangles)

    for edge in collapsible_edges:
        v1, v2 = edge

        # Compute midpoint of the edge
        new_vertex = tuple((new_vertices[v1][i] + new_vertices[v2][i]) / 2 for i in range(3))
        new_vertex_idx = len(new_vertices)

        # Add new vertex to vertices
        new_vertices.append(new_vertex)

        # Update triangles
        updated_triangles = []
        for tri in new_triangles:
            if v1 in tri or v2 in tri:
                # Replace v1 and v2 with the new vertex index
                tri = [new_vertex_idx if v == v1 or v == v2 else v for v in tri]
                if len(set(tri)) == 3:  # Keep only valid triangles
                    updated_triangles.append(tri)
            else:
                updated_triangles.append(tri)
        new_triangles = updated_triangles

    print('-----------------:', compiled, perf_counter() - t)
    return new_vertices, new_triangles


if __name__ == '__main__':
    # compiled: 0.18
    # python:   0.13
    # cythonizer.__autocythonize__ = False

    from ursina import *

    app = Ursina()

    noise = Array2D(width=32, height=32)
    for (x,z), value in enumerate_2d(noise):
        noise[x][z] = random.randint(0,128)

    m = Terrain(height_values=noise)
    m.colors = [hsv(0,0,e.y) for e in m.vertices]
    original_terrain_entity = Entity(model=m, scale=(noise.width,2,noise.height))
    EditorCamera()
    m.triangles = list(chunk_list(m.indices, 3))
    # print(m.triangles)
    m.generate()

    m_low = Mesh()
    Entity(model=m_low, scale=original_terrain_entity.scale, z=noise.height, color=color.azure)

    slider = Slider(min=0, max=180, step=1, default=85, dynamic=False)
    def _on_value_changed():
        # print('decimate', m.vertices, m.triangles)
        # from time import perf_counter
        # t = perf_counter()
        m_low.vertices, m_low.triangles = decimate_mesh_by_angle(m.vertices, list(chunk_list(m.indices, 3)), slider.value)
        # print('----', perf_counter() - t)
        m_low.colors = [hsv(0,0,e[1]) for e in m_low.vertices]
        m_low.generate()
        # print('finished decimating')
    slider.on_value_changed = _on_value_changed

    slider.on_value_changed()


    app.run()