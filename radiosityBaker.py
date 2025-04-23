import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1" #for muting the pygame print at start
import pygame
from pygame.locals import *
from OpenGL.GL import *
import numpy as np
import glm
import argparse

#project's modules
from openGLutils import *
from utils import *
from shaders import *


cubeMapRenderShader = None

"""
Creates a vbo for a baked unit cube, this cube has the same format as the other meshes, but its baked into the code.
The format is a contiguous vertex buffer on base64
"""
def createMultiplierCubeMesh():
    vertices = "AACAvwAAgD8AAIC/AACAPwAAAAAAAAAAAAAAAAAAAAAAAAAAAADAPgAAgD4AAIC/AACAvwAAgD8AAIA/AAAAAAAAAAAAAAAAAAAAAAAAAAAAACA/AAAAAAAAgL8AAIC/AACAvwAAgD8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAwD4AAAAAAACAPwAAgD8AAIC/AAAAAAAAgL8AAAAAAAAAAAAAAAAAAAAAAADAPgAAAD8AAIC/AACAPwAAgD8AAAAAAACAvwAAAAAAAAAAAAAAAAAAAAAAACA/AACAPgAAgL8AAIA/AACAvwAAAAAAAIC/AAAAAAAAAAAAAAAAAAAAAAAAwD4AAIA+AACAPwAAgL8AAIC/AACAvwAAAAAAAAAAAAAAAAAAAAAAAAAAAADAPgAAQD8AAIA/AACAPwAAgD8AAIC/AAAAAAAAAAAAAAAAAAAAAAAAAAAAACA/AAAAPwAAgD8AAIA/AACAvwAAgL8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAwD4AAAA/AACAvwAAgL8AAIC/AAAAAAAAgD8AAAAAAAAAAAAAAAAAAAAAAADAPgAAgD8AAIA/AACAvwAAgD8AAAAAAACAPwAAAAAAAAAAAAAAAAAAAAAAACA/AABAPwAAgD8AAIC/AACAvwAAAAAAAIA/AAAAAAAAAAAAAAAAAAAAAAAAwD4AAEA/AACAvwAAgL8AAIC/AAAAAAAAAAAAAIA/AAAAAAAAAAAAAAAAAAAAPgAAQD8AAIA/AACAPwAAgL8AAAAAAAAAAAAAgD8AAAAAAAAAAAAAAAAAAMA+AAAAPwAAgL8AAIA/AACAvwAAAAAAAAAAAACAPwAAAAAAAAAAAAAAAAAAAD4AAAA/AACAPwAAgL8AAIA/AAAAAAAAAAAAAIC/AAAAAAAAAAAAAAAAAAAgPwAAQD8AAIC/AACAPwAAgD8AAAAAAAAAAAAAgL8AAAAAAAAAAAAAAAAAAGA/AAAAPwAAgD8AAIA/AACAPwAAAAAAAAAAAACAvwAAAAAAAAAAAAAAAAAAID8AAAA/AACAvwAAgD8AAIC/AACAPwAAAAAAAAAAAAAAAAAAAAAAAAAAAADAPgAAgD4AAIC/AACAPwAAgD8AAIA/AAAAAAAAAAAAAAAAAAAAAAAAAAAAACA/AACAPgAAgL8AAIC/AACAPwAAgD8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAID8AAAAAAACAPwAAgD8AAIC/AAAAAAAAgL8AAAAAAAAAAAAAAAAAAAAAAADAPgAAAD8AAIA/AACAPwAAgD8AAAAAAACAvwAAAAAAAAAAAAAAAAAAAAAAACA/AAAAPwAAgL8AAIA/AACAPwAAAAAAAIC/AAAAAAAAAAAAAAAAAAAAAAAAID8AAIA+AACAPwAAgL8AAIC/AACAvwAAAAAAAAAAAAAAAAAAAAAAAAAAAADAPgAAQD8AAIA/AACAvwAAgD8AAIC/AAAAAAAAAAAAAAAAAAAAAAAAAAAAACA/AABAPwAAgD8AAIA/AACAPwAAgL8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAID8AAAA/AACAvwAAgL8AAIC/AAAAAAAAgD8AAAAAAAAAAAAAAAAAAAAAAADAPgAAgD8AAIC/AACAvwAAgD8AAAAAAACAPwAAAAAAAAAAAAAAAAAAAAAAACA/AACAPwAAgD8AAIC/AACAPwAAAAAAAIA/AAAAAAAAAAAAAAAAAAAAAAAAID8AAEA/AACAvwAAgL8AAIC/AAAAAAAAAAAAAIA/AAAAAAAAAAAAAAAAAAAAPgAAQD8AAIA/AACAvwAAgL8AAAAAAAAAAAAAgD8AAAAAAAAAAAAAAAAAAMA+AABAPwAAgD8AAIA/AACAvwAAAAAAAAAAAACAPwAAAAAAAAAAAAAAAAAAwD4AAAA/AACAPwAAgL8AAIA/AAAAAAAAAAAAAIC/AAAAAAAAAAAAAAAAAAAgPwAAQD8AAIC/AACAvwAAgD8AAAAAAAAAAAAAgL8AAAAAAAAAAAAAAAAAAGA/AABAPwAAgL8AAIA/AACAPwAAAAAAAAAAAACAvwAAAAAAAAAAAAAAAAAAYD8AAAA/"
    indices = "AAAAAAEAAAACAAAAAwAAAAQAAAAFAAAABgAAAAcAAAAIAAAACQAAAAoAAAALAAAADAAAAA0AAAAOAAAADwAAABAAAAARAAAAEgAAABMAAAAUAAAAFQAAABYAAAAXAAAAGAAAABkAAAAaAAAAGwAAABwAAAAdAAAAHgAAAB8AAAAgAAAAIQAAACIAAAAjAAAA"
    verticesArray = base64ToFloatArray (vertices)
    indicesArray = base64ToUint32Array (indices)

    meshBuffer = OpenglMeshBuffer(verticesArray, indicesArray)

    multiplierCubeMesh = Mesh()
    multiplierCubeMesh.subMeshes.append(meshBuffer)

    return multiplierCubeMesh

"""
This creates the fbo for the cubemap render texture used on each patch.
"""
def createCubeMapFBO(fboSize = 1024):
    cubemapTexColor = glGenTextures(1)
    glBindTexture(GL_TEXTURE_CUBE_MAP, cubemapTexColor)
    
    for face_idx in range(6):        
        glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + face_idx, 0, formats["RGBA16F"]["internalformat"], 
                    fboSize, fboSize, 0, formats["RGBA16F"]["format"], formats["RGBA16F"]["type"], None)

    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    #Create the depth texture, TODO: see if we can use renderbuffers for this since we are not reading this 
    cubemapTexDepth = glGenTextures(1)
    glBindTexture(GL_TEXTURE_CUBE_MAP, cubemapTexDepth)
    
    for face_idx in range(6):        
        glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + face_idx, 0, GL_DEPTH_COMPONENT, 
                    fboSize, fboSize, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)

    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    #create the FBO
    cubemapFBO = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, cubemapFBO)
    glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, cubemapTexColor, 0)
    glFramebufferTexture(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, cubemapTexDepth, 0)

    if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        print("FRAMEBUFFER NOT COMPLETE!")

    glBindTexture(GL_TEXTURE_CUBE_MAP, 0)
    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    return (cubemapTexColor, cubemapTexDepth, cubemapFBO)

"""
Renders the scene, the cubemap fbo must be bounded previously
There are two types of render, normal and multiplier.
Multiplier type rendering is to render the multiplier texture, I just reused this function for rendering the multiplier really.
"""
def renderHemisphereScene(scene, lightmapsTextures, fboRenderSize, onlyRenderMultiplier, cameraTransform):
    nearPlane = 0.001
    farPlane = 1000.0

    cameraPos = cameraTransform["position"]
    cameraForward = cameraTransform["forwardDir"]
    cameraUp = cameraTransform["upDir"]

    cubemapProj = glm.perspective(glm.radians(90.0), 1.0, nearPlane, farPlane)
    cameraMat = glm.orientation( cameraForward , cameraUp)
    cameraMat = glm.mat3(cameraMat)

    cubemapTransforms = []
    cubemapTransforms.append(glm.lookAt( cameraPos, cameraPos + cameraMat * glm.vec3(1.0, 0.0, 0.0), cameraMat * glm.vec3(0.0, -1.0, 0.0) ) )
    cubemapTransforms.append(glm.lookAt( cameraPos, cameraPos + cameraMat * glm.vec3(-1.0, 0.0, 0.0), cameraMat * glm.vec3(0.0, -1.0, 0.0) ) )
    cubemapTransforms.append(glm.lookAt( cameraPos, cameraPos + cameraMat * glm.vec3(0.0, 1.0, 0.0), cameraMat * glm.vec3(0.0, 0.0, 1.0) ) )
    cubemapTransforms.append(glm.lookAt( cameraPos, cameraPos + cameraMat * glm.vec3(0.0, -1.0, 0.0), cameraMat * glm.vec3(0.0, 0.0, -1.0) ) )
    cubemapTransforms.append(glm.lookAt( cameraPos, cameraPos + cameraMat * glm.vec3(0.0, 0.0, 1.0), cameraMat * glm.vec3(0.0, -1.0, 0.0) ) )
    cubemapTransforms.append(glm.lookAt( cameraPos, cameraPos + cameraMat * glm.vec3(0.0, 0.0, -1.0), cameraMat * glm.vec3(0.0, -1.0, 0.0) ) )

    for idx in range(6):
        setUniformMatrix(cubeMapRenderShader, "cubemapSidesMatrices[" + str(idx) + "]",  cubemapTransforms[idx])
    
    setUniformVec3(cubeMapRenderShader, "cameraUp", cameraUp)
    setUniformVec3(cubeMapRenderShader, "cameraPos", cameraPos)
    setUniformMatrix(cubeMapRenderShader, "projMat", cubemapProj)
    setUniformFloat(cubeMapRenderShader, "texResolution", fboRenderSize)

    #Clean the fbo from previous iterations
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  

    for obj in scene["sceneObjects"]:
        meshName = obj["mesh"]
        meshToRender = scene["meshes"][meshName]
        lightmapName = obj["lightmapTexName"]
        
        # Deal with lightmaps
        if lightmapName in lightmapsTextures:
            lightmapTex = lightmapsTextures[lightmapName]["openglTex"]
            glActiveTexture(GL_TEXTURE1) 
            glBindTexture(GL_TEXTURE_2D, lightmapTex.textureId)
            glUniform1i(glGetUniformLocation(cubeMapRenderShader, "lightmap"), 1)
        else:
            glActiveTexture(GL_TEXTURE1) 
            glBindTexture(GL_TEXTURE_2D, 0)
            glUniform1i(glGetUniformLocation(cubeMapRenderShader, "lightmap"), 1)

        for subMesh in meshToRender.subMeshes:
            setUniformMatrix(cubeMapRenderShader, "modelMat", obj["transform"])
            #setUniformVec2(cubeMapRenderShader, "lightmapTiling", glm.vec2(obj["lightmapUVTiling"][0], obj["lightmapUVTiling"][1]))
            #setUniformVec2(cubeMapRenderShader, "lightmapOffset", glm.vec2(obj["lightmapUVOffset"][0], obj["lightmapUVOffset"][1]))
            setUniformInt(cubeMapRenderShader, "renderType", 0)

            if onlyRenderMultiplier:
                setUniformInt(cubeMapRenderShader, "renderType", 2)

            subMesh.bind()
            glDrawElements(GL_TRIANGLES, subMesh.indicesAmount, GL_UNSIGNED_INT, None )
            subMesh.unbind()

    if not onlyRenderMultiplier:
        for light in scene["lights"]:
            meshName = light["mesh"]
            meshToRender = scene["meshes"][meshName]

            for subMesh in meshToRender.subMeshes:
                setUniformMatrix(cubeMapRenderShader, "modelMat", light["transform"])
                setUniformInt(cubeMapRenderShader, "renderType", 1)
                setUniformFloat(cubeMapRenderShader, "lightIntensity", light["intensity"])

                subMesh.bind()
                glDrawElements(GL_TRIANGLES, subMesh.indicesAmount, GL_UNSIGNED_INT, None )
                subMesh.unbind()

"""
Calculates the final color pixel of each pass, sums all of the pixels(which al ready have the multplier applied to them in the shader) and divides them by the multiplier 
"""
def calculateTexelLightValue(cubemapFBO, multiplerCompensationValue, fboRenderSize = 256):
    colorValue = glm.vec3(0.0,0.0,0.0)

    for idx in range(6):
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_CUBE_MAP_POSITIVE_X+idx, cubemapFBO[0], 0)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_CUBE_MAP_POSITIVE_X+idx, cubemapFBO[1], 0)

        data = glReadPixels(0, 0, fboRenderSize, fboRenderSize, formats["RGBA16F"]["format"], formats["RGBA16F"]["type"])
        cubemapColorData = np.frombuffer(data, dtype = formats["RGBA16F"]["npType"]).reshape(fboRenderSize, fboRenderSize, 4)

        accumulation = cubemapColorData.sum(axis=(0, 1)) 
        colorValue += glm.vec3(accumulation[0], accumulation[1], accumulation[2])

    colorValue /= multiplerCompensationValue

    glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, cubemapFBO[0], 0)
    glFramebufferTexture(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, cubemapFBO[1], 0)

    return colorValue

"""
Calculates the value that divides the sum of all the pixels for each patch.
"""
def calculateMultiplierDivisorValue(cubemapFBO, fboRenderSize = 256):
    value = 0.0
    for idx in range(6):
        
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_CUBE_MAP_POSITIVE_X+idx, cubemapFBO[0], 0)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_CUBE_MAP_POSITIVE_X+idx, cubemapFBO[1], 0)

        data = glReadPixels(0, 0, fboRenderSize, fboRenderSize, formats["RGBA16F"]["format"], formats["RGBA16F"]["type"])
        cubemapColorData = np.frombuffer(data, dtype = formats["RGBA16F"]["npType"]).reshape(fboRenderSize, fboRenderSize, 4)

        accumulation = cubemapColorData.sum(axis=(0, 1)) 
        value += accumulation[0]

    glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, cubemapFBO[0], 0)
    glFramebufferTexture(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, cubemapFBO[1], 0)

    return value       
 
"""
Does the radiosity render along with its iterations and outputs the textures to disk. First we calculate the multiplier texture's divisor for a given texture size
This function receives the lightmapsData dict which contains all of the info for each lightmap patch, like its position, normal etc...
We iterate through all of the patches rendering the scene and then calculating the texel color value, saving the image after each iteration.
"""
def radiosityRender(scene, lightmapsData, outputPath, iterationsNum = 5, fboRenderSize = 256):

    global cubeMapRenderShader
    cubeMapRenderShader = createShaderProgramGeometry(cubemapVshader, cubemapFshader, cubemapGshader)


    glViewport(0, 0, fboRenderSize, fboRenderSize)
    cubemapFBO = createCubeMapFBO(fboRenderSize)

    #Common opengl commands needed for rendering these scenes
    glUseProgram(cubeMapRenderShader)
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE) 

    #Bind fbo framebuffer
    glBindFramebuffer(GL_FRAMEBUFFER, cubemapFBO[2])
    glDrawBuffer(GL_COLOR_ATTACHMENT0)
    glReadBuffer(GL_COLOR_ATTACHMENT0)

    multiplierCubeScene = {
        'meshes': {'multiplierCube': createMultiplierCubeMesh()},
        'sceneObjects': [{'mesh': 'multiplierCube', 
                                "position": [0.0,0.0,0.0],
                                "rotation": [0.0,0.0,0.0],
                                "scale": [1.0,1.0,1.0],
                                "transform": createTransform([0.0,0.0,0.0],[0.0,0.0,0.0],[1.0,1.0,1.0]),
                                "lightmapUVTiling": [1.0,1.0],
                                "lightmapUVOffset": [0.0,0.0],
                                "lightmapTexName": ""
                                }
                               ],
        'lights': [],
    }

    cubeSceneCameraTransform = {
                            "position": glm.vec3(0.0,0.0,0.0),
                            "forwardDir": glm.vec3(0.0,1.0,0.0),
                            "upDir": glm.vec3(0.0,0.0,1.0)
                        }
    
    # We need to render the only a scene with a unit cube first, so we can calculate the divisor of the multplier described by Hugo Elias ,
    renderHemisphereScene(multiplierCubeScene, {}, fboRenderSize, True, cubeSceneCameraTransform)
    multiplerDivisorValue = calculateMultiplierDivisorValue(cubemapFBO, fboRenderSize)
    #print ("Multiplier Divisor: " + str(multiplerDivisorValue))

    #Rebind cubemapFBO
    glBindFramebuffer(GL_FRAMEBUFFER, cubemapFBO[2])
    glDrawBuffer(GL_COLOR_ATTACHMENT0)
    glReadBuffer(GL_COLOR_ATTACHMENT0)
    
    finalLightmaps = {}
    #-----Normal Render 
    for iteration in range(iterationsNum):
        #update or create lightmap textures previous each iteration:
        for lightmapTexName in lightmapsData:
            if lightmapTexName not in finalLightmaps:
                renderTexSize = lightmapsData[lightmapTexName]["texSize"]
                imgData = np.zeros((renderTexSize, renderTexSize, 3), dtype= np.float32)
                CurrentLightmapTex = {
                    "data": imgData,
                    "openglTex": OpenGLTexture(renderTexSize, renderTexSize, formats["RGB32F"], imgData)
                }
                finalLightmaps[lightmapTexName] = CurrentLightmapTex
            else:
                CurrentLightmapTex = finalLightmaps[lightmapTexName]
                imgData = CurrentLightmapTex["data"]
                openglTex = CurrentLightmapTex["openglTex"]
                openglTex.update(imgData, GL_TEXTURE1)

        for lightmapTexName in lightmapsData:
            interpPos = lightmapsData[lightmapTexName]["pos"]  
            interpNormal = lightmapsData[lightmapTexName]["normal"]
            objectsId = lightmapsData[lightmapTexName]["objId"] 
            renderTexSize = lightmapsData[lightmapTexName]["texSize"]
            
            imgData = finalLightmaps[lightmapTexName]["data"]

            for pixI in range(renderTexSize):
                for pixJ in range(renderTexSize):

                    pixelPosition = glm.vec3(interpPos[pixI][pixJ])
                    pixelNormal = glm.vec3(interpNormal[pixI][pixJ])
                    pixelId = objectsId[pixI][pixJ]

                    if pixelId[0] > 0.05:
                        cameraForward = glm.vec3(1.0,0.0,0.0)
                        
                        dotProdValue = glm.dot(cameraForward, glm.normalize(pixelNormal))
                        if abs(dotProdValue) >= 0.999:
                            cameraForward = glm.vec3(0.0,1.0,0.0)

                        cameraForward = glm.cross(cameraForward,  glm.normalize(pixelNormal))    

                        cameraTransform = {
                            "position": pixelPosition,
                            "forwardDir": cameraForward,
                            "upDir": glm.normalize(pixelNormal)
                        }   

                        renderHemisphereScene(
                            scene,
                            finalLightmaps, 
                            fboRenderSize,
                            False,
                            cameraTransform
                        )
                        
                        finalColorValue = calculateTexelLightValue(cubemapFBO, multiplerDivisorValue, fboRenderSize)

                        finalPixel = np.array([finalColorValue.r, finalColorValue.g, finalColorValue.b])# * 255
                        imgData[pixI][pixJ] = finalPixel
                print (f"Progress {lightmapTexName}, Pass# {iteration+1}:    {pixI} / {renderTexSize}")

        for lightmapTexName in lightmapsData:
            renderTexSize = lightmapsData[lightmapTexName]["texSize"]
            imgData = finalLightmaps[lightmapTexName]["data"]

            #scaledArray = imgData * 255.0
            #scaledArray = np.clip(scaledArray, 0, 255)
            #uint8Array = scaledArray.astype(np.uint8)

            imgData = imgData.astype(np.float32)
            fileName = os.path.basename(lightmapTexName)
            saveExr(outputPath + fileName + "_" + str(iteration+1), imgData)
            #savePng(outputPath + "radiosityRender" + fileName + str(iterations), uint8Array, "RGB")

def parseArgs():
    parser = argparse.ArgumentParser(description="Radiosity Light Baker")
    parser.add_argument('-s', '--scenePath', type=str, required=True, help='Path to scene file (e.g., scene.json)')
    parser.add_argument('-r', '--resourcesPath', type=str, required=True, help='Path to mesh resources')
    parser.add_argument('-o', '--outputPath', type=str, required=True, help='Directory to output rendered images')
    parser.add_argument("-q", "--cubemapQuality", type=int, default=128, help="Resolution of cubemap face in pixels (default: 128).")
    parser.add_argument("-i", "--iterations", type=int, default=5, help="Number of iterations/bounces that the algorithm renders (default: 5).")
    return parser.parse_args()

def main():
    args = parseArgs()
    if not os.path.isfile(args.scenePath):
        raise FileNotFoundError(f"Scene file not found: {args.scenePath}")
    
    if not os.path.isdir(args.resourcesPath):
        raise NotADirectoryError(f"Resources path not found: {args.resourcesPath}")
    
    if not os.path.isdir(args.outputPath):
        os.makedirs(args.outputPath)

    pygame.init()

    display = (100, 100)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL | HIDDEN)

    scene = getSceneInformation(args.resourcesPath, args.scenePath)
    lightmapsData = calculateRasterizedInformation(scene)

    #This saves the alpha mask of the image to disk
    for lightmapTexName in lightmapsData:
        idData = lightmapsData[lightmapTexName]["objId"]
        scaledArray = idData * 255.0
        scaledArray = np.clip(scaledArray, 0, 255)
        uint8Array = scaledArray.astype(np.uint8)
        savePng(args.outputPath + lightmapTexName +"_mask", uint8Array, "RGB")

    radiosityRender(scene, lightmapsData, args.outputPath, args.iterations, args.cubemapQuality)

    pygame.quit()

if __name__ == "__main__":
    main()