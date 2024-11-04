# test_example = true
from wgpu_shadertoy import Shadertoy

shader_code = """
// Customizable parameters
const TAU: f32 = 2.0 * 3.14159;
const TIME_SCALE: f32 = 0.2;  // Animation speed
const SHAPE_DISTORTION: f32 = 1.2;  // Shape distortion
const COLOR_SHIFT: f32 = 0.7;  // Color variation
const ROTATION_SPEED: f32 = 0.5;  // Rotation speed
const INTENSITY: f32 = 1.5;  // Brightness
const SPIRAL_FACTOR: f32 = 2.0;  // Spiral intensity
const MORPH_SPEED: f32 = 0.3;  // Shape morphing speed

fn palette(t: f32) -> vec3<f32> {
    // Modified color palette for more varied colors
    let a = vec3<f32>(0.5, 0.5, 0.5);
    let b = vec3<f32>(0.5, 0.5, 0.5);
    let c = vec3<f32>(1.0, 1.0, 1.0);
    let d = vec3<f32>(0.263 + COLOR_SHIFT, 0.416 + COLOR_SHIFT * 0.5, 0.657 + sin(t * 0.2) * 0.3);
    return a + b * cos(4.0 * (c * t + d));
}

fn rotation(angle: f32) -> mat2x2<f32> {
    let modified_angle = angle * ROTATION_SPEED;
    return mat2x2<f32>(cos(modified_angle), -sin(modified_angle), 
                      sin(modified_angle), cos(modified_angle));
}

fn spiral_dist(p: vec2<f32>, r: f32) -> f32 {
    let theta = atan2(p.y, p.x);
    let spiral = length(p) - r - sin(theta * SPIRAL_FACTOR + i_time * TIME_SCALE) * 0.2;
    return spiral;
}

fn morph_shape(pos: vec2<f32>, r: f32, time: f32) -> f32 {
    var p = pos * SHAPE_DISTORTION;
    
    // Create morphing between different shapes
    let morph = sin(time * MORPH_SPEED) * 0.5 + 0.5;
    
    // Spiral distance
    let spiral = spiral_dist(p, r);
    
    // Hexagonal distance
    let angle = TAU / 6.0;
    let hex_p = vec2<f32>(
        cos(floor(0.5 + atan2(p.y, p.x) / angle) * angle),
        sin(floor(0.5 + atan2(p.y, p.x) / angle) * angle)
    );
    let hex = abs(dot(normalize(hex_p), p)) - r;
    
    // Smooth interpolation between spiral and hex
    return mix(spiral, hex, morph);
}

fn shader_main(frag_coord: vec2<f32>) -> vec4<f32> {
    var uv = (frag_coord * 2.0 - vec2<f32>(i_resolution.xy)) / i_resolution.y;
    let uv0 = uv;
    var finalColor = vec3<f32>(0.0);

    // Add spiral distortion to UV coordinates
    let dist = length(uv);
    let angle = atan2(uv.y, uv.x);
    let spiral_warp = sin(dist * 10.0 - i_time * TIME_SCALE) * 0.1;
    uv = uv * (1.0 + spiral_warp);

    for (var i: f32 = 0.0; i < 4.0; i += 1.0) {
        var col2 = vec3<f32>(0.0);
        let t = fract(0.1 * i_time * TIME_SCALE * 0.51);
        
        // Add wave distortion
        let wave = sin(uv.x * 5.0 + i_time * TIME_SCALE) * cos(uv.y * 5.0 + i_time * TIME_SCALE) * 0.1;
        uv = uv + vec2<f32>(wave);
        
        let rot1 = rotation(3.0 * TAU * (0.3 - clamp(length(uv), 0.0, 0.3)));
        uv = vec2<f32>(uv.x * rot1[0][0] + uv.y * rot1[0][1], 
                       uv.x * rot1[1][0] + uv.y * rot1[1][1]);
        
        var s = -1.0;
        for (var j: f32 = 0.0; j < 5.0; j += 1.0) {
            let rad = 1.4 / pow(2.0, j) * (0.9 - 0.2 * j);
            
            let rot2 = rotation(-2.0 * s * (j + 1.0) * TAU * t);
            uv = vec2<f32>(uv.x * rot2[0][0] + uv.y * rot2[0][1],
                          uv.x * rot2[1][0] + uv.y * rot2[1][1]);
            
            // Use our new morphing shape instead of triangles
            let shape = morph_shape(uv, rad, i_time);
            s *= -1.0;
            col2 += 1.004 / abs(shape);
        }

        uv = fract(uv * 1.5) - vec2<f32>(0.5);
        var d = length(uv) * exp(-length(uv0));
        
        // Add time-varying color modulation
        let time_factor = sin(i_time * TIME_SCALE * 0.5) * 0.5 + 0.5;
        let col = palette(length(uv0) + i * 0.4 + i_time * TIME_SCALE * 0.4 + time_factor);

        d = sin(d * 8.0 + i_time * TIME_SCALE) / 8.0;
        d = abs(d);
        d = pow(0.01 / d, 1.2);
        
        // Add pulsing intensity
        let pulse = sin(i_time * TIME_SCALE * 0.5) * 0.2 + 1.0;
        finalColor += col * d * INTENSITY * pulse;
    }

    // Add subtle color cycling to the final output
    let cycle = sin(i_time * TIME_SCALE * 0.2) * 0.1 + 1.0;
    finalColor *= vec3<f32>(cycle, cycle * 0.9, cycle * 1.1);

    return vec4<f32>(finalColor, 1.0);
}
"""

shader = Shadertoy(shader_code, resolution=(800, 450))

if __name__ == "__main__":
    shader.show()