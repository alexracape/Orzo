import os
import numpy as np
import moderngl
from moderngl_window.scene import MeshProgram
from moderngl_window.geometry import sphere
from PIL import Image

current_dir = os.path.dirname(__file__)

def print_program_info(program):
    # Print all uniforms
    print("Uniforms:")
    for uniform in program.uniforms.values():
        print(f"Name: {uniform.name}, Type: {uniform.type}, Size: {uniform.array_length}")

    # Print all attributes
    print("Attributes:")
    for attr in program.attributes.values():
        print(f"Name: {attr.name}, Type: {attr.array_length}")

class PhongProgram(MeshProgram):
    def __init__(self, wnd, num_instances, **kwargs):
        super().__init__(program=None)
        self.window = wnd
        ctx = wnd.ctx
        self.num_instances = num_instances

        # Load shaders
        vertex_shader_path = os.path.join(current_dir, "shaders/phong_vertex.glsl")
        fragment_shader_path = os.path.join(current_dir, "shaders/phong_fragment.glsl")

        with open(vertex_shader_path, 'r') as file:
            vertex_shader_code = file.read()
        with open(fragment_shader_path, 'r') as file:
            fragment_shader_code = file.read()

        # Compile shaders
        try:
            self.program = ctx.program(vertex_shader=vertex_shader_code, fragment_shader=fragment_shader_code)
        except moderngl.Error as e:
            print(f"Shader compilation failed: {e}")

        # Default texture setup
        img = Image.open(os.path.join(current_dir, "resources/default.png"))
        self.default_texture = ctx.texture(img.size, 4, img.tobytes())
        self.default_texture.repeat_x = False
        self.default_texture.repeat_y = False

    def draw(self, mesh, projection_matrix, model_matrix, camera_matrix, time=0):
        # Set the projection, model, and camera matrices
        self.program['m_proj'].write(projection_matrix.tobytes())
        self.program['m_model'].write(model_matrix.tobytes())
        self.program['m_cam'].write(camera_matrix.tobytes())
        self.program['camera_position'].value = tuple(camera_matrix[:3, 3])  # Camera world position

        # Handle material properties if the mesh has a material
        # if mesh.material:
        #     self.program['material_color'].value = tuple(mesh.material.color)
        #     self.program['double_sided'].value = mesh.material.double_sided
        #     if mesh.material.mat_texture:
        #         mesh.material.mat_texture.texture.use()
        #     else:
        #         self.default_texture.use()
        # else:
        #     self.program['material_color'].value = (1.0, 0.0, 0.0, 1.0)
        #     self.program['double_sided'].value = False
        #     self.default_texture.use()

        # Render the mesh (the VAO should handle drawing and program binding)
        mesh.vao.render(self.program)

    def apply(self, mesh):
        return self

class FrameSelectProgram(MeshProgram):
    def __init__(self, wnd, num_instances, **kwargs):
        super().__init__(program=None)
        self.window = wnd
        ctx = wnd.ctx
        self.num_instances = num_instances

        # Load shaders
        vertex_shader_path = os.path.join(current_dir, "shaders/select_vertex.glsl")
        fragment_shader_path = os.path.join(current_dir, "shaders/select_fragment.glsl")

        with open(vertex_shader_path, 'r') as file:
            vertex_shader_code = file.read()
        with open(fragment_shader_path, 'r') as file:
            fragment_shader_code = file.read()

        self.program = ctx.program(vertex_shader=vertex_shader_code, fragment_shader=fragment_shader_code)

    def draw(self, mesh, projection_matrix, model_matrix, camera_matrix, time=0):
        # Prepare uniforms
        self.program['m_proj'].write(projection_matrix.tobytes())
        self.program['m_model'].write(model_matrix.tobytes())
        self.program['m_cam'].write(camera_matrix.tobytes())
        self.program['id'].value = mesh.entity_id  # Ensure mesh.entity_id is an integer
        self.program['hit_value'].value = 1  # Simulated hit value, should be an integer

        # Render the mesh
        mesh.vao.render(self.program)

    def apply(self, mesh):
        return self
