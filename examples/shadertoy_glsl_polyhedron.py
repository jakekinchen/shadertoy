from wgpu_shadertoy import Shadertoy

shader_code = """
const PI: f32 = 3.14159265359;

fn rotateX(angle: f32) -> mat3x3<f32> {
    let s = sin(angle);
    let c = cos(angle);
    return mat3x3<f32>(
        vec3<f32>(1.0, 0.0, 0.0),
        vec3<f32>(0.0, c, -s),
        vec3<f32>(0.0, s, c)
    );
}

fn rotateY(angle: f32) -> mat3x3<f32> {
    let s = sin(angle);
    let c = cos(angle);
    return mat3x3<f32>(
        vec3<f32>(c, 0.0, s),
        vec3<f32>(0.0, 1.0, 0.0),
        vec3<f32>(-s, 0.0, c)
    );
}

fn rotateZ(angle: f32) -> mat3x3<f32> {
    let s = sin(angle);
    let c = cos(angle);
    return mat3x3<f32>(
        vec3<f32>(c, -s, 0.0),
        vec3<f32>(s, c, 0.0),
        vec3<f32>(0.0, 0.0, 1.0)
    );
}

fn palette(t: f32, phase: f32) -> vec3<f32> {
    let a = vec3<f32>(0.8, 0.4, 0.5);
    let b = vec3<f32>(0.2, 0.5, 0.5);
    let c = vec3<f32>(1.0, 1.0, 1.0);
    let d = vec3<f32>(0.0, 0.3, 0.6);

    let color = a + b * cos(2.0 * PI * (c * t + d + phase));
    return mix(color, vec3<f32>(1.2, 1.2, 1.2), smoothstep(0.2, 0.0, t) * 0.7);
}

fn sdTorus(p: vec3<f32>, t: vec2<f32>) -> f32 {
    let q = vec2<f32>(length(vec2<f32>(p.x, p.z)) - t.x, p.y);
    return length(q) - t.y;
}

fn map(p: vec3<f32>, time: f32) -> vec2<f32> {
    var pos = p;

    // Complex rotation
    let rotTime1 = time * 0.5;
    let rotTime2 = time * 0.3;
    let rotTime3 = time * 0.7;

    pos = rotateX(rotTime1 + sin(time * 0.2) * 0.5) * pos;
    pos = rotateY(rotTime2 + cos(time * 0.3) * 0.5) * pos;
    pos = rotateZ(rotTime3 + sin(time * 0.4) * 0.5) * pos;

    // Twist the space
    let twist = sin(time * 0.2) * 0.5;
    let len_xz = length(vec2<f32>(pos.x, pos.z));
    let angle = len_xz * twist + time;
    let c = cos(angle);
    let s = sin(angle);

    pos = vec3<f32>(
        c * pos.x - s * pos.z,
        pos.y,
        s * pos.x + c * pos.z
    );

    // Base shape - twisted torus
    var d1 = sdTorus(pos, vec2<f32>(1.5 + sin(time * 0.3) * 0.2, 0.3));

    // Add variation
    d1 += sin(pos.x * 8.0 + time) * sin(pos.y * 6.0) * sin(pos.z * 4.0) * 0.1;

    return vec2<f32>(d1, 1.0);
}

fn rayMarch(ro: vec3<f32>, rd: vec3<f32>, time: f32) -> vec4<f32> {
    var t = 0.0;
    var m = -1.0;

    for(var i = 0; i < 128; i++) {
        let pos = ro + rd * t;
        let h = map(pos, time);

        if(h.x < 0.001) {
            m = h.y;
            break;
        }

        t += h.x * 0.5;  // Slower stepping for better detail

        if(t > 20.0) {
            break;
        }
    }

    return vec4<f32>(t, m, 0.0, 0.0);
}

fn calcNormal(pos: vec3<f32>, time: f32) -> vec3<f32> {
    let e = vec2<f32>(0.001, 0.0);
    return normalize(vec3<f32>(
        map(pos + vec3<f32>(e.x, e.y, e.y), time).x - map(pos - vec3<f32>(e.x, e.y, e.y), time).x,
        map(pos + vec3<f32>(e.y, e.x, e.y), time).x - map(pos - vec3<f32>(e.y, e.x, e.y), time).x,
        map(pos + vec3<f32>(e.y, e.y, e.x), time).x - map(pos - vec3<f32>(e.y, e.y, e.x), time).x
    ));
}

fn shader_main(frag_coord: vec2<f32>) -> vec4<f32> {
    let uv = (frag_coord * 2.0 - vec2<f32>(i_resolution.xy)) / i_resolution.y;

    // Camera
    let time = i_time * 0.5;
    let camDist = 4.0 + sin(time * 0.3) * 0.5;
    let camPos = vec3<f32>(
        sin(time * 0.3) * camDist,
        cos(time * 0.4) * 2.0,
        cos(time * 0.3) * camDist
    );
    let camTarget = vec3<f32>(0.0, 0.0, 0.0);
    let camUp = normalize(vec3<f32>(0.0, 1.0, 0.0));

    // Camera matrix
    let camDir = normalize(camTarget - camPos);
    let camRight = normalize(cross(camUp, camDir));
    let camUp2 = cross(camDir, camRight);

    // Ray direction
    let fieldOfView = 60.0;
    let rd = normalize(
        camRight * uv.x +
        camUp2 * uv.y +
        camDir * (1.0 / tan(fieldOfView * 0.5 * PI / 180.0))
    );

    // Ray marching
    let rm = rayMarch(camPos, rd, time);

    var color = vec3<f32>(0.0);

    if(rm.y > -0.5) {
        let pos = camPos + rd * rm.x;
        let normal = calcNormal(pos, time);

        // Base color from normal and position
        let phase = length(pos) * 0.5 + time;
        var col = palette(length(pos) * 0.3 + time * 0.2, phase);

        // Lighting
        let light = normalize(vec3<f32>(sin(time), 1.0, cos(time)));
        let diff = max(dot(normal, light), 0.0);
        let spec = pow(max(dot(reflect(-light, normal), -rd), 0.0), 32.0);

        // Fresnel
        let fresnel = pow(1.0 - max(dot(normal, -rd), 0.0), 4.0);

        // Final color composition
        color = col * (diff * 0.7 + 0.3);
        color += vec3<f32>(1.0, 0.7, 0.3) * spec;
        color += vec3<f32>(0.2, 0.5, 1.0) * fresnel;

        // Add glow
        let glow = exp(-rm.x * 0.2) * 0.5;
        color += col * glow;
    }

    // Fog and atmosphere
    color = mix(color, vec3<f32>(0.0), 1.0 - exp(-rm.x * 0.15));

    // Bloom
    color += pow(color, vec3<f32>(2.0)) * 0.5;

    // Tone mapping and gamma correction
    color = color / (1.0 + color);
    color = pow(color, vec3<f32>(0.4545));

    return vec4<f32>(color, 1.0);
}
"""

shader = Shadertoy(shader_code, resolution=(800, 450))

if __name__ == "__main__":
    shader.show()