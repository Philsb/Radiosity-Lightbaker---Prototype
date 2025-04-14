
uv_raster_vshader = """
#version 330 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;
layout(location = 2) in vec3 color;
layout(location = 3) in vec2 uv;

uniform mat4 modelMat;
uniform mat4 viewMat;
uniform mat4 projMat;

uniform vec2 lightmapTiling;
uniform vec2 lightmapOffset;

smooth out vec3 fragNormal; 
smooth out vec3 fragPos; 

void main()
{
    vec2 uv_coords = (lightmapTiling* uv ) + lightmapOffset;

    //world space coordinates
    fragNormal = mat3(transpose(inverse(modelMat))) * normal;
    fragPos = ( modelMat * vec4(position, 1.0) ).xyz;

    gl_Position =  vec4( mix(-1.0,1.0,uv_coords.x), mix(-1.0,1.0,uv_coords.y), 1.0, 1.0);

}
"""

uv_raster_fshader = """
#version 330 core

smooth in vec3 fragNormal; 
smooth in vec3 fragPos;

uniform uvec2 objId;

layout(location = 0) out vec3 posColor;  
layout(location = 1) out vec3 normalColor;  
layout(location = 2) out uvec3 idColor;  


void main()
{
    posColor = fragPos;
    normalColor = normalize(fragNormal);
    idColor = uvec3(objId.x, objId.y, 0u );
}
"""


cubemap_vshader = """
#version 330 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;
layout(location = 2) in vec3 color;
layout(location = 3) in vec2 uv;

uniform mat4 modelMat;

out DATA
{
    vec3 fragNormal;
    vec3 fragColor;
    vec2 fragUv;
} data_out;


void main()
{
    data_out.fragNormal = mat3(transpose(inverse(modelMat))) * normal;
    data_out.fragColor = color;
    data_out.fragUv = uv;
    gl_Position = modelMat * vec4(position, 1.0);
}  

"""


cubemap_gshader = """
#version 330 core
layout (triangles) in;
layout (triangle_strip, max_vertices=18) out;

uniform mat4 cubemapSidesMatrices[6];
uniform mat4 projMat;

smooth out vec4 fragPos; 
smooth out vec3 fragNormal; 
smooth out vec3 fragColor; 
smooth out vec2 fragUv;

out vec3 cubeForward;


in DATA
{
    vec3 fragNormal;
    vec3 fragColor;
    vec2 fragUv;

} data_in[];

vec3 getCameraForward(mat4 viewMatrix)
{
    return -normalize(vec3(viewMatrix[0][2], viewMatrix[1][2], viewMatrix[2][2]));
}

void main()
{
    for(int face = 0; face < 6; ++face)
    {
        gl_Layer = face; // built-in variable that specifies to which face we render.
        for(int i = 0; i < 3; ++i) // for each triangle vertex
        {
            fragPos = gl_in[i].gl_Position;
            fragNormal = data_in[i].fragNormal;
            fragColor = data_in[i].fragColor;
            fragUv = data_in[i].fragUv;
            cubeForward = getCameraForward(cubemapSidesMatrices[face]);
            gl_Position = projMat * cubemapSidesMatrices[face] * fragPos;
            EmitVertex();
        }    
        EndPrimitive();
    }
}
"""

cubemap_fshader = """
#version 330 core
in vec3 fragNormal; 
in vec3 fragColor; 
in vec4 fragPos; 
in vec2 fragUv;

//This is needed for calculating the cube distortion compensation
in vec3 cubeForward;

layout(location = 0) out vec4 diffuseColor;

uniform vec3 color;
uniform int isLight;
uniform float lightIntensity;

uniform vec3 cameraUp;
uniform vec3 cameraPos;

uniform float texResolution;

uniform vec2 lightmapTiling;
uniform vec2 lightmapOffset;

uniform sampler2D tex1;
uniform sampler2D lightmap;


float getCubeCompensation()
{
    vec2 coords = (gl_FragCoord.xy/texResolution) - vec2(0.5, 0.5) ;
    float dist = distance( vec3(0.0, 0.0, 0.0), vec3( coords * 2.0 , 1.0) );
    return 1.0/(dist*dist);
}

float getDistanceCompensation()
{
    float dist = distance(cameraPos, fragPos.xyz);
    return 1.0/(dist*dist);
}


void main()
{
    float discardValue = dot( normalize(fragPos.xyz - cameraPos) , cameraUp) > 0.0 ? 1.0 : 0.0;
    float distortionCompensation = dot ( cubeForward, normalize(fragPos.xyz - cameraPos) );
    float lambertLaw = dot ( cameraUp, normalize(fragPos.xyz - cameraPos));

    float generalCompensation = getCubeCompensation() * lambertLaw * distortionCompensation ;

    if (isLight == 0)
    {
        float dotProd = dot(  normalize(fragNormal) , normalize( vec3(0.0,1.0,0.2) ) );
        float lightDotVal = (1.0 + dotProd) / 2.0;

        vec3 textureColor = texture(tex1, fragUv).rgb;
        vec3 lightmapColor = texture(lightmap, (fragUv * lightmapTiling) + lightmapOffset).rgb;

        float backFaceBlackValue = dot( normalize(fragNormal) , normalize(fragPos.xyz - cameraPos));
        backFaceBlackValue = backFaceBlackValue <= 0.005 ? 1.0 : 0.0;

        diffuseColor = vec4(fragColor * 1.0 * lightmapColor * generalCompensation * backFaceBlackValue, 1.0) * discardValue;

    }
    else if (isLight == 1) {
        diffuseColor = vec4(color * lightIntensity * generalCompensation, 1.0) * discardValue;
    }
    else if (isLight == 2) {

        vec2 coords = gl_FragCoord.xy/texResolution;

        diffuseColor = vec4(vec3(1.0,1.0,1.0) * generalCompensation, 1.0) * discardValue;
    }
    
    
}  

"""