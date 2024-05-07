#version 330

in vec3 in_position;    // Vertex position
in vec3 in_normal;      // Vertex normal

uniform mat4 m_proj;    // Projection matrix
uniform mat4 m_model;   // Model matrix
uniform mat4 m_cam;     // Camera matrix
uniform vec4 material_color; // Uniform for color

out vec4 vColor;        // Pass color to fragment shader

void main() {
    gl_Position = m_proj * m_cam * m_model * vec4(in_position, 1.0);
    vColor = material_color;  // Use the uniform color
}