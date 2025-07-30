# cubeforge/model.py
import logging
from .constants import CubeAnchor
from .writers import get_writer # Use the generalized writer system

# --- Logging Configuration Removed ---
# Get a logger instance for this module. Configuration is left to the application.
logger = logging.getLogger(__name__)


class VoxelModel:
    """
    Represents a 3D model composed of voxels.
    Each voxel can have independent dimensions (width, height, depth).

    Allows adding voxels based on coordinates and anchor points, and exporting
    the resulting shape using various mesh writers. Logging messages are emitted
    via the standard 'logging' module; configuration is up to the application.
    """
    def __init__(self, voxel_dimensions=(1.0, 1.0, 1.0)):
        """
        Initializes the VoxelModel.

        Args:
            voxel_dimensions (tuple): A tuple of three positive numbers
                                     (width, height, depth) representing the
                                     default size of each voxel.
        """
        if not (isinstance(voxel_dimensions, (tuple, list)) and
                len(voxel_dimensions) == 3 and
                all(isinstance(dim, (int, float)) and dim > 0 for dim in voxel_dimensions)):
            raise ValueError("voxel_dimensions must be a tuple or list of three positive numbers (width, height, depth).")
        self.voxel_dimensions = tuple(float(dim) for dim in voxel_dimensions)
        # Stores voxel data as a dictionary:
        # key: integer grid coordinate (ix, iy, iz)
        # value: tuple of dimensions (width, height, depth) for that voxel
        self._voxels = {}
        logger.info(f"VoxelModel initialized with default voxel_dimensions={self.voxel_dimensions}")

    def _calculate_min_corner(self, x, y, z, anchor, dimensions):
        """
        Calculates the minimum corner coordinates based on anchor point and voxel dimensions.

        Internal helper method used by add_voxel and remove_voxel.

        Args:
            x (float): X-coordinate of the anchor point.
            y (float): Y-coordinate of the anchor point.
            z (float): Z-coordinate of the anchor point.
            anchor (CubeAnchor): The anchor type.
            dimensions (tuple): The (width, height, depth) of the voxel.

        Returns:
            tuple: (min_x, min_y, min_z) coordinates of the voxel's minimum corner.

        Raises:
            ValueError: If an invalid anchor point is provided.
        """
        size_x, size_y, size_z = dimensions
        half_x, half_y, half_z = size_x / 2.0, size_y / 2.0, size_z / 2.0

        if anchor == CubeAnchor.CORNER_NEG:
            min_x, min_y, min_z = x, y, z
        elif anchor == CubeAnchor.CENTER:
            min_x, min_y, min_z = x - half_x, y - half_y, z - half_z
        elif anchor == CubeAnchor.CORNER_POS:
            min_x, min_y, min_z = x - size_x, y - size_y, z - size_z
        elif anchor == CubeAnchor.BOTTOM_CENTER: # Center of Min Y face
            min_x, min_y, min_z = x - half_x, y, z - half_z
        elif anchor == CubeAnchor.TOP_CENTER: # Center of Max Y face
            min_x, min_y, min_z = x - half_x, y - size_y, z - half_z
        else:
            raise ValueError(f"Invalid anchor point: {anchor}")

        return min_x, min_y, min_z

    def add_voxel(self, x, y, z, anchor=CubeAnchor.CORNER_NEG, dimensions=None):
        """
        Adds a voxel to the model. Replaces add_cube.

        Args:
            x (float): X-coordinate of the voxel's anchor point.
            y (float): Y-coordinate of the voxel's anchor point.
            z (float): Z-coordinate of the voxel's anchor point.
            anchor (CubeAnchor): The reference point within the voxel that
                                (x, y, z) corresponds to. Defaults to
                                CubeAnchor.CORNER_NEG.
            dimensions (tuple, optional): The (width, height, depth) for this
                                          specific voxel. If None, the model's
                                          default dimensions are used.
        """
        voxel_dims = self.voxel_dimensions if dimensions is None else tuple(float(d) for d in dimensions)
        if dimensions is not None and not (isinstance(voxel_dims, (tuple, list)) and
                                           len(voxel_dims) == 3 and
                                           all(isinstance(d, (int, float)) and d > 0 for d in voxel_dims)):
            raise ValueError("Custom dimensions must be a tuple or list of three positive numbers.")

        min_x, min_y, min_z = self._calculate_min_corner(x, y, z, anchor, voxel_dims)

        # Calculate grid coordinates based on minimum corner and *default* dimensions
        # This ensures voxels snap to a consistent grid.
        grid_x = round(min_x / self.voxel_dimensions[0])
        grid_y = round(min_y / self.voxel_dimensions[1])
        grid_z = round(min_z / self.voxel_dimensions[2])

        grid_coord = (grid_x, grid_y, grid_z)
        self._voxels[grid_coord] = voxel_dims
        # logger.debug(f"Added voxel at grid {grid_coord} (from anchor {anchor} at ({x},{y},{z}))")

    # Alias add_cube to add_voxel for backward compatibility (optional, but can be helpful)
    add_cube = add_voxel

    def add_voxels(self, coordinates, anchor=CubeAnchor.CORNER_NEG, dimensions=None):
        """
        Adds multiple voxels from an iterable. Replaces add_cubes.

        Args:
            coordinates (iterable): An iterable of (x, y, z) tuples or lists.
            anchor (CubeAnchor): The anchor point to use for all voxels added
                                in this call.
            dimensions (tuple, optional): The dimensions to apply to all voxels
                                          in this call. If None, defaults are used.
        """
        for x_coord, y_coord, z_coord in coordinates:
            self.add_voxel(x_coord, y_coord, z_coord, anchor, dimensions)

    # Alias add_cubes to add_voxels
    add_cubes = add_voxels

    def remove_voxel(self, x, y, z, anchor=CubeAnchor.CORNER_NEG):
        """
        Removes a voxel from the model based on its anchor coordinates. Replaces remove_cube.

        Args:
            x (float): X-coordinate of the voxel's anchor point.
            y (float): Y-coordinate of the voxel's anchor point.
            z (float): Z-coordinate of the voxel's anchor point.
            anchor (CubeAnchor): The reference point within the voxel that
                                (x, y, z) corresponds to.
        """
        # Note: Removal does not need custom dimensions, as it identifies the
        # voxel by its position on the grid, which is calculated using default dimensions.
        min_x, min_y, min_z = self._calculate_min_corner(x, y, z, anchor, self.voxel_dimensions)

        grid_x = round(min_x / self.voxel_dimensions[0])
        grid_y = round(min_y / self.voxel_dimensions[1])
        grid_z = round(min_z / self.voxel_dimensions[2])

        grid_coord = (grid_x, grid_y, grid_z)
        if grid_coord in self._voxels:
            del self._voxels[grid_coord]
        # logger.debug(f"Attempted removal at grid {grid_coord}")

    # Alias remove_cube to remove_voxel
    remove_cube = remove_voxel

    def clear(self):
        """Removes all voxels from the model."""
        self._voxels.clear()
        logger.info("VoxelModel cleared.")

    def generate_mesh(self):
        """
        Generates a list of triangles representing the exposed faces of the voxels.

        Ensures consistent counter-clockwise winding order (right-hand rule)
        for outward-facing normals.

        Returns:
            list: A list of tuples, where each tuple is a triangle defined as
                (normal, vertex1, vertex2, vertex3). Coordinates are in
                the model's world space. Returns an empty list if no voxels
                have been added.
        """
        if not self._voxels:
            return []

        logger.info(f"Generating mesh for {len(self._voxels)} voxels...")
        triangles = []
        # Voxel dimensions are now fetched per-voxel, so size_x, etc. are defined inside the loop.

        # Define faces by normal, neighbor offset, and vertex indices (0-7)
        # Vertex indices correspond to relative positions scaled by dimensions:
        # 0: (0,0,0), 1: (Wx,0,0), 2: (0,Hy,0), 3: (Wx,Hy,0)
        # 4: (0,0,Dz), 5: (Wx,0,Dz), 6: (0,Hy,Dz), 7: (Wx,Hy,Dz)
        # Indices are ordered CCW when looking from outside the voxel.
        faces_data = [
            # Normal, Neighbor Offset, Vertex Indices (Tri1: v0,v1,v2; Tri2: v0,v2,v3)
            ((1, 0, 0), (1, 0, 0), [1, 3, 7, 5]), # +X face
            ((-1, 0, 0), (-1, 0, 0), [4, 6, 2, 0]), # -X face
            ((0, 1, 0), (0, 1, 0), [2, 6, 7, 3]), # +Y face
            ((0, -1, 0), (0, -1, 0), [0, 1, 5, 4]), # -Y face
            ((0, 0, 1), (0, 0, 1), [4, 5, 7, 6]), # +Z face
            ((0, 0, -1), (0, 0, -1), [3, 1, 0, 2]), # -Z face
        ]

        processed_faces = 0
        for (gx, gy, gz), (size_x, size_y, size_z) in self._voxels.items():
            # Calculate the minimum corner based on grid coordinates and *default* dimensions
            min_cx = gx * self.voxel_dimensions[0]
            min_cy = gy * self.voxel_dimensions[1]
            min_cz = gz * self.voxel_dimensions[2]

            # Calculate the 8 absolute vertex coordinates for this voxel using its specific dimensions
            verts = [
                (min_cx + (i % 2) * size_x, min_cy + ((i // 2) % 2) * size_y, min_cz + (i // 4) * size_z)
                for i in range(8)
            ]

            for normal, offset, indices in faces_data:
                neighbor_coord = (gx + offset[0], gy + offset[1], gz + offset[2])
                neighbor_dims = self._voxels.get(neighbor_coord)

                # A face is exposed if there is no neighbor, OR if the neighbor
                # has different dimensions, which would create a complex partial
                # surface. For simplicity and correctness of the outer shell,
                # we will generate the face in the latter case.
                if not neighbor_dims or neighbor_dims != (size_x, size_y, size_z): # Exposed face
                    processed_faces += 1
                    # Get the four vertices for this face using the indices
                    v0 = verts[indices[0]]
                    v1 = verts[indices[1]]
                    v2 = verts[indices[2]]
                    v3 = verts[indices[3]]
                    # Create two triangles with correct CCW winding
                    triangles.append((normal, v0, v1, v2)) # Triangle 1
                    triangles.append((normal, v0, v2, v3)) # Triangle 2

        logger.info(f"Mesh generation complete. Found {processed_faces} exposed faces, resulting in {len(triangles)} triangles.")
        return triangles

    def save_mesh(self, filename, format='stl_binary', **kwargs):
        """
        Generates the mesh and saves it to a file using the specified format.

        Args:
            filename (str): The path to the output file.
            format (str): The desired output format identifier (e.g/,
                        'stl_binary', 'stl_ascii'). Case-insensitive.
                        Defaults to 'stl_binary'.
            **kwargs: Additional arguments passed directly to the specific
                    file writer (e.g., 'solid_name' for STL formats).
        """
        triangles = self.generate_mesh()
        if not triangles:
            logger.warning("No voxels in the model. Mesh file will not be generated.")
            return

        try:
            writer = get_writer(format)
            writer.write(triangles, filename, **kwargs)
            # No need for logger.info here, the writer handles its own success message
        except ValueError as e:
            logger.error(f"Failed to save mesh: {e}")
            raise
        except Exception as e:
            logger.error(f"An error occurred during mesh saving to '{filename}': {e}")
            raise
