# test_example = true
from wgpu_shadertoy import Shadertoy

shader_code = """
const TAU: f32 = 2.0 * 3.14159;

fn rot2(a: f32) -> mat2x2<f32> {
    let c = cos(a);
    let s = sin(a);
    return mat2x2<f32>(c, -s, s, c);
}

fn palette(t: f32) -> vec3<f32> {
    // Enhanced red-blue contrast
    let a = vec3<f32>(0.8, 0.4, 0.5);
    let b = vec3<f32>(0.2, 0.4, 0.2);
    let c = vec3<f32>(2.0, 1.0, 1.0);
    let d = vec3<f32>(0.0, 0.25, 0.25);
    
    let phase = sin(i_time * 0.1) * 0.4;
    return a + b * cos(TAU * (c * t + d + phase));
}

fn glow(d: f32, intensity: f32, thickness: f32) -> f32 {
    // Enhanced volumetric glow
    return pow(thickness / (d * d + 0.001), intensity) * 1.2;
}

fn shader_main(frag_coord: vec2<f32>) -> vec4<f32> {
    var uv = (frag_coord * 2.0 - vec2<f32>(i_resolution.xy)) / i_resolution.y;
    
    // Enhanced camera movement
    let zoom = 1.4 + sin(i_time * 0.2) * 0.4;
    uv *= zoom;
    uv *= rot2(i_time * 0.15);  // Slower rotation for better depth perception
    
    let uv0 = uv;
    var finalColor = vec3<f32>(0.0);
    
    // Layered 3D effect
    for (var i: f32 = 0.0; i < 6.0; i += 1.0) {
        uv *= rot2(0.3 + i_time * 0.05);
        uv = fract(uv * 1.5) - vec2<f32>(0.5);

        var d = length(uv) * exp(-length(uv0));
        
        // Enhanced depth-based coloring
        let col = palette(length(uv0) + i * 0.4 + i_time * 0.4);
        
        let wave = sin(i_time + i * 0.5) * 0.2;
        d = sin(d * (8.0 + wave) + i_time) / 2.0;
        d = abs(d);
        
        // Thicker, more volumetric structures
        let base_thickness = 0.02 + sin(i_time * 0.2) * 0.005;
        let intensity = 1.2 + sin(i_time * 0.3 + i * 0.2) * 0.2;
        let thickness = base_thickness * (1.0 + sin(i_time + i) * 0.3);
        
        let glow_factor = glow(d, intensity, thickness);
        
        // Enhanced color mixing for better red-blue contrast
        let mix_factor = sin(i_time * 0.2 + i * 0.5) * 0.4 + 0.6;
        finalColor = mix(finalColor, finalColor + col * glow_factor * 1.8, mix_factor);
    }
    
    // Enhanced glow and contrast
    let pulse = 1.2 + sin(i_time * 0.5) * 0.3;
    finalColor *= pulse;
    
    // Softer vignette for depth
    let vignette = 1.0 - pow(length(uv0) * 0.65, 2.0);
    finalColor *= vignette;
    
    // Add bloom for enhanced glow
    finalColor += pow(finalColor, vec3<f32>(2.0)) * 0.4;
    
    // Color correction for vibrant red-blue contrast
    finalColor = pow(finalColor, vec3<f32>(0.8));
    
    // Prevent oversaturation while preserving glow
    finalColor = finalColor / (1.0 + length(finalColor) * 0.3);
        
    return vec4<f32>(finalColor, 1.0);
}
"""

shader = Shadertoy(shader_code, resolution=(800, 450))

if __name__ == "__main__":
    shader.show()