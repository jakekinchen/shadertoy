# test_example = true
from wgpu_shadertoy import Shadertoy

shader_code = """
const TAU: f32 = 2.0 * 3.14159;

fn kaleidoscope(p: vec2<f32>, segments: f32) -> vec2<f32> {
    var angle = atan2(p.y, p.x);
    let radius = length(p);
    
    // Fix: use % instead of mod
    angle = angle % (TAU / segments);
    angle = abs(angle - TAU / segments / 2.0);
    
    return vec2<f32>(cos(angle), sin(angle)) * radius;
}

fn palette(t: f32) -> vec3<f32> {
    let a = vec3<f32>(0.5, 0.5, 0.5);
    let b = vec3<f32>(0.5, 0.5, 0.5);
    let c = vec3<f32>(1.0, 1.0, 1.0);
    let d = vec3<f32>(0.263, 0.416, 0.557);
    
    // Rainbow color cycling
    let rainbow = vec3<f32>(
        sin(t * 1.0 + i_time),
        sin(t * 1.1 + i_time * 1.1),
        sin(t * 1.2 + i_time * 1.2)
    ) * 0.15;
    
    return a + b * cos(TAU * (c * t + d)) + rainbow;
}

fn shader_main(frag_coord: vec2<f32>) -> vec4<f32> {
    var uv = (frag_coord * 2.0 - vec2<f32>(i_resolution.xy)) / i_resolution.y;
    
    // Dynamic number of kaleidoscope segments
    let segments = 6.0 + sin(i_time * 0.2) * 2.0;
    uv = kaleidoscope(uv, segments);
    
    let uv0 = uv;
    var finalColor = vec3<f32>(0.0);
    
    for (var i: f32 = 0.0; i < 8.0; i += 1.0) {
        uv = kaleidoscope(uv * 1.5, segments) - vec2<f32>(0.5);

        var d = length(uv) * exp(-length(uv0));
        
        // Spiral effect
        let angle = atan2(uv.y, uv.x);
        d += sin(angle * 3.0 + i_time) * 0.1;

        let col = palette(length(uv0) + i * 0.4 + i_time * 0.4);

        d = sin(d * 12.0 + i_time) / 2.0;
        d = abs(d);
        d = pow(0.005 / d, 1.2);

        // Add interference patterns
        let interference = sin(d * 30.0 + i_time) * 0.5 + 0.5;
        finalColor += col * d * interference;
    }
    
    // Add bloom effect
    let bloom = smoothstep(0.5, 1.0, length(finalColor));
    finalColor += finalColor * bloom * 0.5;
        
    return vec4<f32>(finalColor, 1.0);
}
"""

shader = Shadertoy(shader_code, resolution=(800, 450))

if __name__ == "__main__":
    shader.show()