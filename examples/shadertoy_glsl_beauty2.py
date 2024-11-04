# test_example = true
from wgpu_shadertoy import Shadertoy

shader_code = """
const PI: f32 = 3.14159265359;

fn rot2(a: f32) -> mat2x2<f32> {
    let c = cos(a);
    let s = sin(a);
    return mat2x2<f32>(c, -s, s, c);
}

fn glow(d: f32, intensity: f32, thickness: f32) -> f32 {
    // Enhanced volumetric glow with softer falloff
    let base = thickness / (d * d + 0.00001);
    return pow(base, intensity) * (1.0 + 0.2 * sin(d * 30.0 + i_time));
}

fn palette(t: f32, phase: f32) -> vec3<f32> {
    // Enhanced color palette for richer reds and blues
    let a = vec3<f32>(0.8, 0.4, 0.5);
    let b = vec3<f32>(0.2, 0.5, 0.5);
    let c = vec3<f32>(1.0, 1.0, 1.0);
    let d = vec3<f32>(0.0, 0.3, 0.6);
    
    let color = a + b * cos(2.0 * PI * (c * t + d + phase));
    
    // Add white-hot core
    let intensity = smoothstep(0.2, 0.0, t);
    return mix(color, vec3<f32>(1.2, 1.2, 1.2), intensity * 0.7);
}

fn shader_main(frag_coord: vec2<f32>) -> vec4<f32> {
    var uv = (frag_coord * 2.0 - vec2<f32>(i_resolution.xy)) / i_resolution.y;
    
    // Enhanced camera movement
    let zoom = 1.5 + sin(i_time * 0.2) * 0.3;
    uv *= zoom;
    
    // Multiple rotation layers
    let baseRot = i_time * 0.15;
    uv *= rot2(baseRot);
    
    let uv0 = uv;
    var finalColor = vec3<f32>(0.0);
    
    // Multiple interacting layers
    for (var i: f32 = 0.0; i < 8.0; i += 1.0) {
        var localUV = uv;
        
        // Spiral transformation
        let angle = i * PI / 4.0 + i_time * (0.1 + i * 0.02);
        localUV *= rot2(angle);
        
        // Create spiral effect
        localUV = fract(localUV * (1.4 + i * 0.1)) - 0.5;
        
        // Calculate distance field
        var d = length(localUV) * exp(-length(uv0) * 0.3);
        
        // Add wave distortion
        let wave = sin(i_time + i * 0.5) * 0.2;
        d = sin(d * (6.0 + wave) + i_time * 0.5) / 2.0;
        d = abs(d);
        
        // Enhanced thickness and glow
        let base_thickness = 0.02 + 0.005 * sin(i_time + i);
        let intensity = 1.1 + 0.2 * sin(i_time * 0.3 + i * 0.2);
        let glow_factor = glow(d, intensity, base_thickness);
        
        // Color variation
        let phase = i * 0.5 + i_time * 0.2;
        var col = palette(length(uv0) + i * 0.2 + i_time * 0.2, phase);
        
        // Layer blending
        let blend = smoothstep(0.5, 0.0, d) * (1.0 - i * 0.1);
        col *= glow_factor * 1.5;
        
        // Add color bleeding
        let bleed = pow(glow_factor, 1.5) * 0.3;
        col += vec3<f32>(0.2, 0.0, 0.4) * bleed;
        
        finalColor += col * blend;
    }
    
    // Add depth and atmosphere
    let depth = exp(-length(uv0) * 1.5);
    finalColor *= depth;
    
    // Enhanced bloom
    let bloom = pow(finalColor, vec3<f32>(2.0)) * 0.5;
    finalColor += bloom;
    
    // Color correction and contrast
    finalColor = pow(finalColor, vec3<f32>(0.8));
    finalColor = finalColor / (1.0 + finalColor);
    
    // Add subtle color shift at edges
    let edge = 1.0 - smoothstep(0.0, 2.0, length(uv0));
    finalColor += vec3<f32>(0.1, 0.0, 0.2) * edge;
    
    return vec4<f32>(finalColor, 1.0);
}
"""

shader = Shadertoy(shader_code, resolution=(800, 450))

if __name__ == "__main__":
    shader.show()