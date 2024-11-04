# test_example = true
from wgpu_shadertoy import Shadertoy

shader_code = """
const TAU: f32 = 2.0 * 3.14159;

fn palette(t: f32) -> vec3<f32> {
    let a = vec3<f32>(0.5, 0.5, 0.5);
    let b = vec3<f32>(0.5, 0.5, 0.5);
    let c = vec3<f32>(1.0, 1.0, 1.0);
    let d = vec3<f32>(0.263, 0.416, 0.557);
    
    // Add subtle color pulsing
    let pulse = sin(i_time * 0.2) * 0.2;
    return a + b * cos(TAU * (c * t + d)) * (1.0 + pulse);
}

fn glow(d: f32, intensity: f32) -> f32 {
    // Softer falloff for more ethereal glow
    return pow(0.01 / (d * d + 0.001), intensity);
}

fn shader_main(frag_coord: vec2<f32>) -> vec4<f32> {
    var uv = (frag_coord * 2.0 - vec2<f32>(i_resolution.xy)) / i_resolution.y;
    let uv0 = uv;
    var finalColor = vec3<f32>(0.0);
    
    // Add subtle rotation
    let angle = i_time * 0.1;
    let rot_mat = mat2x2<f32>(
        cos(angle), -sin(angle),
        sin(angle), cos(angle)
    );
    uv *= rot_mat;
    
    for (var i: f32 = 0.0; i < 8.0; i += 1.0) {
        uv = fract(uv * 1.5) - vec2<f32>(0.5);

        var d = length(uv) * exp(-length(uv0));

        let col = palette(length(uv0) + i * 0.4 + i_time * 0.4);

        // Slower wave movement for more ethereal look
        d = sin(d * 8.0 + i_time * 0.5) / 2.0;
        d = abs(d);

        // Dynamic glow intensity
        let base_intensity = 1.2;
        let intensity_variation = sin(i_time * 0.3 + i * 0.2) * 0.2;
        let glow_factor = glow(d, base_intensity + intensity_variation);

        // Add extra glow for inner iterations
        let inner_glow = exp(-i * 0.2) * 1.5;
        
        finalColor += col * glow_factor * inner_glow;
    }
    
    // Add bloom effect
    let bloom = pow(finalColor, vec3<f32>(2.0));
    finalColor = mix(finalColor, bloom, 0.4);
    
    // Add subtle pulsing to final color
    let pulse = 1.0 + sin(i_time * 0.4) * 0.15;
    finalColor *= pulse;
    
    // Add soft vignette
    let vignette = 1.0 - pow(length(uv0) * 0.65, 2.0);
    finalColor *= vignette;
    
    // Add outer glow
    let outer_glow = exp(-length(uv0) * 2.0) * 0.5;
    finalColor += vec3<f32>(outer_glow);
    
    // Prevent oversaturation while preserving glow
    finalColor = finalColor / (1.0 + length(finalColor) * 0.3);
    
    // Enhance contrast slightly
    finalColor = pow(finalColor, vec3<f32>(0.9));
        
    return vec4<f32>(finalColor, 1.0);
}
"""

shader = Shadertoy(shader_code, resolution=(800, 450))

if __name__ == "__main__":
    shader.show()