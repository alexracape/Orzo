#version 330

in vec3 frag_normal;
in vec3 frag_position;
in vec2 frag_texcoord;

uniform sampler2D base_texture;
uniform vec3 camera_position;
uniform vec4 material_color;  // Declaration for material color
uniform int num_lights;
uniform bool double_sided;  // Uniform to control double-sided materials

struct LightInfo {
    vec3 position;
    vec3 color;
    float intensity;
};

uniform LightInfo lights[8];

out vec4 frag_color;

void main() {
    vec3 normal = normalize(frag_normal);
    vec3 view_dir = normalize(camera_position - frag_position);
    vec4 tex_color = texture(base_texture, frag_texcoord);
    vec3 result = vec3(0.0);

    // Adjust normal if double-sided material is used
    if (double_sided && gl_FrontFacing == false) {
        normal = -normal;  // Invert the normal if rendering the back face
    }

    for (int i = 0; i < num_lights; ++i) {
        vec3 light_dir = normalize(lights[i].position - frag_position);
        float diff = max(dot(normal, light_dir), 0.0);
        vec3 reflect_dir = reflect(-light_dir, normal);
        float spec = pow(max(dot(view_dir, reflect_dir), 0.0), 32.0);
        result += lights[i].intensity * (lights[i].color * diff + vec3(1.0) * spec);
    }

    // Combine calculated light with texture color and modulate by the material color
    frag_color = vec4((normalize(frag_normal) + 1.0) * 0.5, 1.0);
    //frag_color = vec4(1.0, 1.0, 0.0, 1.0); 
}