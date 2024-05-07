#version 330

uniform int id; // Object ID as integer
uniform int hit_value; // Hit value to indicate interaction type

out vec4 f_color; // Output color that encodes selection data

void main() {
    // Encode the ID and hit value into the red and green components, respectively
    float encoded_id = float(id) / 255.0;  // Normalize assuming max ID value < 255
    float encoded_hit = float(hit_value) / 255.0;  // Normalize assuming max hit value < 255
    f_color = vec4(encoded_id, encoded_hit, 0.0, 1.0);  // Blue and alpha channels can be used for other data or set to constants
   // f_color = vec4(1.0, 0.0, 0.0, 1.0);
}