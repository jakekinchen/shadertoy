from wgpu_shadertoy import Shadertoy

shader_code = """
const PI: f32 = 3.14159265359;

fn rotate2d(angle: f32) -> mat2x2<f32> {
    return mat2x2<f32>(
        cos(angle), -sin(angle),
        sin(angle), cos(angle)
    );
}

fn getColor(p: vec3<f32>) -> vec3<f32> {
    var pos = abs(p);  // Make pattern symmetrical
    
    // Scale and transform the coordinate space
    pos *= 1.25;
    pos = 0.5 * pos / dot(pos, pos);
    
    // Add time-based movement
    pos += 0.072 * i_time;
    
    // Base pattern parameter
    let t = 0.13 * length(pos);
    
    // Start with base color
    var col = vec3<f32>(0.3, 0.4, 0.5);
    
    // Layer multiple frequency cosine waves with different phases and colors
    col += 0.12 * cos(6.28318 * t * 1.0 + vec3<f32>(0.0, 0.8, 1.1));
    col += 0.11 * cos(6.28318 * t * 3.1 + vec3<f32>(0.3, 0.4, 0.1));
    col += 0.10 * cos(6.28318 * t * 5.1 + vec3<f32>(0.1, 0.7, 1.1));
    col += 0.10 * cos(6.28318 * t * 17.1 + vec3<f32>(0.2, 0.6, 0.7));
    col += 0.10 * cos(6.28318 * t * 31.1 + vec3<f32>(0.1, 0.6, 0.7));
    col += 0.10 * cos(6.28318 * t * 65.1 + vec3<f32>(0.0, 0.5, 0.8));
    col += 0.10 * cos(6.28318 * t * 115.1 + vec3<f32>(0.1, 0.4, 0.7));
    col += 0.10 * cos(6.28318 * t * 265.1 + vec3<f32>(1.1, 1.4, 2.7));
    
    return clamp(col, vec3<f32>(0.0), vec3<f32>(1.0));
}

fn shader_main(frag_coord: vec2<f32>) -> vec4<f32> {
    // Normalize coordinates
    var uv = (frag_coord * 2.0 - vec2<f32>(i_resolution.xy)) / i_resolution.y;
    
    // Add rotation
    let rotation = i_time * 0.2;
    uv *= rotate2d(rotation);
    
    // Create dynamic zoom
    let zoom = 1.0 + sin(i_time * 0.2) * 0.3;
    uv *= zoom;
    
    var finalColor = getColor(vec3<f32>(uv, 0.0));
    
    // Add pulsing effect
    let pulse = 1.0 + sin(i_time * 0.5) * 0.2;
    finalColor *= pulse;
    
    // Add vignette
    let vignette = 1.0 - length(uv) * 0.5;
    finalColor *= vignette;
    
    return vec4<f32>(finalColor, 1.0);
}
"""

shader = Shadertoy(shader_code, resolution=(800, 450))

if __name__ == "__main__":
    shader.show()