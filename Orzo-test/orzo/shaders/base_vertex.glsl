#version 330

in vec3 in_position;
in vec3 in_normal;
in vec2 in_texture;

uniform mat4 m_proj;
uniform mat4 m_model;
uniform mat4 m_cam;
uniform vec3 camera_position;

out vec4 color;
out vec3 normal;
out vec3 world_position;
out vec2 texcoord;
out vec3 view_vector;
out float instance_id;

void main() {
    vec4 local_position = vec4(in_position, 1.0);
    gl_Position = m_proj * m_cam * m_model * local_position;

    mat3 normal_matrix = mat3(m_model);
    normal = normalize(normal_matrix * in_normal);

    // Procedural coloring based on normal direction
    color = vec4(abs(normal), 1.0); // Convert normal components to absolute values to ensure positive colors

    world_position = (m_model * local_position).xyz;
    view_vector = camera_position - world_position;
    texcoord = in_texture; // Assuming texture coordinates are used elsewhere for texture mapping

    instance_id = 0.0; // For potential use in instanced rendering
}