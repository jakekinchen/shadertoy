# test_example = true
from wgpu_shadertoy import Shadertoy

shader_code = """
// Customizable parameters
const TAU: f32 = 2.0 * 3.14159;

fn palette(t: f32) -> vec3<f32> {
    let a = vec3<f32>(0.5, 0.5, 0.5);
    let b = vec3<f32>(0.5, 0.5, 0.5);
    let c = vec3<f32>(1.0, 1.0, 1.0);
    let d = vec3<f32>(0.263, 0.416, 0.557);

    return a + b * cos(TAU * (c * t + d));
}

fn shader_main(frag_coord: vec2<f32>) -> vec4<f32> {
    var uv = (frag_coord * 2.0 - vec2<f32>(i_resolution.xy)) / i_resolution.y;
    let uv0 = uv;
    var finalColor = vec3<f32>(0.0);
    
    for (var i: f32 = 0.0; i < 4.0; i += 1.0) {
        uv = fract(uv * 1.5) - vec2<f32>(0.5);

        var d = length(uv) * exp(-length(uv0));

        let col = palette(length(uv0) + i * 0.4 + i_time * 0.4);

        d = sin(d * 8.0 + i_time) / 8.0;
        d = abs(d);

        d = pow(0.01 / d, 1.2);

        finalColor += col * d;
    }
        
    return vec4<f32>(finalColor, 1.0);
}
"""

shader = Shadertoy(shader_code, resolution=(800, 450))

if __name__ == "__main__":
    shader.show()