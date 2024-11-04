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
    // Reduced base brightness to allow for more color variation
    let a = vec3<f32>(0.3, 0.3, 0.3);  // Reduced from 0.5
    let b = vec3<f32>(0.4, 0.4, 0.4);  // Reduced from 0.5
    let c = vec3<f32>(1.0, 1.0, 1.0);
    let d = vec3<f32>(0.263, 0.416, 0.557);
    
    let phase = sin(i_time * 0.1) * 0.4;
    // Removed the * 1.5 amplification to prevent oversaturation
    return a + b * cos(TAU * (c * t + d + phase));
}

fn glow(d: f32, intensity: f32, thickness: f32) -> f32 {
    // Softened glow falloff for better color preservation
    let glow_value = thickness / (d * d + 0.01);  // Added small epsilon to prevent division by zero
    return pow(glow_value, intensity) * 0.8;  // Scaled down intensity
}

fn shader_main(frag_coord: vec2<f32>) -> vec4<f32> {
    var uv = (frag_coord * 2.0 - vec2<f32>(i_resolution.xy)) / i_resolution.y;
    
    let zoom = 1.2 + sin(i_time * 0.2) * 0.3;
    uv *= zoom;
    uv *= rot2(i_time * 0.1);
    
    let uv0 = uv;
    var finalColor = vec3<f32>(0.0);
    
    for (var i: f32 = 0.0; i < 9.0; i += 1.0) {
        uv *= rot2(0.2 + i_time * 0.05);
        uv = fract(uv * 1.5) - vec2<f32>(0.5);

        var d = length(uv) * exp(-length(uv0));
        
        // Enhanced color variation with depth
        let col = palette(length(uv0) + i * 0.4 + i_time * 0.4);
        
        let wave = sin(i_time + i * 0.5) * 0.2;
        d = sin(d * (8.0 + wave) + i_time) / 2.0;
        d = abs(d);
        
        // Adjusted thickness and intensity for better color preservation
        let base_thickness = 0.015;  // Slightly reduced
        let intensity = 1.2 + sin(i_time * 0.3 + i * 0.2) * 0.2;  // Reduced from 1.4
        let thickness = base_thickness * (1.0 + sin(i_time + i) * 0.3);
        
        let glow_factor = glow(d, intensity, thickness);
        
        // More gradual color mixing
        let mix_factor = sin(i_time * 0.2 + i * 0.5) * 0.4 + 0.6;  // Adjusted range
        finalColor = mix(finalColor, finalColor + col * glow_factor, mix_factor);
    }
    
    // Gentler pulse
    let pulse = 1.1 + sin(i_time * 0.5) * 0.2;  // Reduced from 1.2/0.3
    finalColor *= pulse;
    
    let vignette = 1.0 - pow(length(uv0) * 0.7, 2.0);
    finalColor *= vignette;
    
    // Reduced bloom intensity and added color preservation
    let bloom = pow(finalColor, vec3<f32>(2.0)) * 0.25;  // Reduced from 0.4
    finalColor = mix(finalColor, finalColor + bloom, 0.7);
    
    // Color correction and saturation adjustment
    finalColor = pow(finalColor, vec3<f32>(0.9));  // Slightly reduced contrast
    
    // Prevent oversaturation while preserving color
    finalColor = finalColor / (1.0 + length(finalColor) * 0.3);
        
    return vec4<f32>(finalColor, 1.0);
}
"""
shader = Shadertoy(shader_code, resolution=(800, 450))

if __name__ == "__main__":
    shader.show()