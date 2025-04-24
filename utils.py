import base64
import glm
import numpy as np
from PIL import Image
import json
from openGLutils import *
from shaders import *
import pyexr


"""
This program utilizes a simple but custom mesh format, each mesh vertex buffer is stored in a json as a base64 string this function retrieves that buffer.
"""
def base64ToFloatArray(base64_string: str) -> np.ndarray:
    decodedBytes = base64.b64decode(base64_string)
    floatArray = np.frombuffer(decodedBytes, dtype=np.float32)
    return floatArray

"""
Same as above but for the indices and it transforms them into uint32
"""
def base64ToUint32Array(base64_string: str) -> np.ndarray:
    decodedBytes = base64.b64decode(base64_string)
    uint32Array = np.frombuffer(decodedBytes, dtype=np.uint32)
    return uint32Array

def eulerToMat4(yaw: float, pitch: float, roll: float) -> glm.quat:
    # Create quaternions from yaw, pitch, and roll
    qYaw = glm.angleAxis(yaw, glm.vec3(0.0, 1.0, 0.0))  # Yaw around Y-axis
    qPitch = glm.angleAxis(pitch, glm.vec3(1.0, 0.0, 0.0))  # Pitch around X-axis
    qRoll = glm.angleAxis(roll, glm.vec3(0.0, 0.0, 1.0))  # Roll around Z-axis

    # Combine the quaternions
    quaternion = qRoll * qPitch * qYaw  # Note the order of multiplication
    return glm.mat4_cast(glm.normalize(quaternion))

def createTransform(pos, rot, scale):
    posMat = glm.translate(glm.mat4(1.0), glm.vec3(pos[0], pos[1], pos[2]))  
    rotMat = eulerToMat4(rot[0], rot[1], rot[2])
    scaleMat = glm.scale(glm.mat4(1.0), glm.vec3(scale[0], scale[1], scale[2]))
    
    return posMat * rotMat * scaleMat

"""
For the rasterized info stage we create an fbo with the color outputs, position, normal and Id,
id is the image that differentiates between the uv islands, in other words the alpha map
"""
def createRasterInfoFBO(tex_size):
    #RENDER TEXTURE
    posTexture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, posTexture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB32F, tex_size, tex_size, 0, GL_RGB, GL_FLOAT, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glBindTexture(GL_TEXTURE_2D, 0)

    normalTexture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, normalTexture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB32F, tex_size, tex_size, 0, GL_RGB, GL_FLOAT, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glBindTexture(GL_TEXTURE_2D, 0)

    idTexture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, idTexture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB32UI, tex_size, tex_size, 0, GL_RGB_INTEGER, GL_UNSIGNED_INT, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glBindTexture(GL_TEXTURE_2D, 0)
    
    #DEPTH BUFFER
    depthBuffer = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, depthBuffer)
    # Create the depth buffer's storage
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, tex_size, tex_size)
   
    #FRAME BUFFER
    fbo = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, fbo);  

    #ATTACH COLOR TEXTURES along with depthBuffer
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, posTexture, 0)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT1, GL_TEXTURE_2D, normalTexture, 0)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT2, GL_TEXTURE_2D, idTexture, 0)
    
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, depthBuffer)

    attachments = [GL_COLOR_ATTACHMENT0,GL_COLOR_ATTACHMENT1,GL_COLOR_ATTACHMENT2]
    glDrawBuffers(3, attachments)

    if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        checkFramebufferStatus()
        return (0,0,0)
    
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    glBindRenderbuffer(GL_RENDERBUFFER, 0)
    return ([posTexture, normalTexture, idTexture], depthBuffer, fbo)

"""
This is a very important stage, we need to rasterize the lightmap patches as textures, along with a bunch of info like position, normal etc...
For this we take advantage of opengl and raster the scene but projected into its uv coordinates along the screen.
"""
def calculateRasterizedInformation(scene):
    lightmapsFrameBuffers = {}
    for obj in scene["sceneObjects"]:
        lightmapName = obj["lightmapTexName"]
        lightmapSize = obj["lightmapSize"]
        if lightmapName not in lightmapsFrameBuffers:
            lightmapsFrameBuffers[lightmapName] = createRasterInfoFBO(lightmapSize)

    shaderRasterPos = createShaderProgram(uvRasterVshader, uvRasterFshader)
    glUseProgram(shaderRasterPos) 
    #Rasterize into UV space stage-----------------------
    # Initialize OpenGL settings
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glDisable(GL_BLEND) 
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)          

    for obj in scene["sceneObjects"]:
        meshName = obj["mesh"]
        meshToRender = scene["meshes"][meshName]

        lightmapTexName = obj["lightmapTexName"]
        lightmapSize = obj["lightmapSize"]
        lightmapFrameBuff = lightmapsFrameBuffers[lightmapTexName]

        glViewport(0, 0, lightmapSize, lightmapSize)
        glBindFramebuffer(GL_FRAMEBUFFER, lightmapFrameBuff[2])

        for subMesh in meshToRender.subMeshes:
            setUniformMatrix(shaderRasterPos, "modelMat", obj["transform"])
            setUniformMatrix(shaderRasterPos, "viewMat", glm.mat4(1.0))
            setUniformMatrix(shaderRasterPos, "projMat", glm.perspective(90.0, 1.0, 0.01, 1000.0))

            #setUniformVec2(shaderRasterPos, "lightmapTiling", glm.vec2(obj["lightmapUVTiling"][0], obj["lightmapUVTiling"][1]))
            #setUniformVec2(shaderRasterPos, "lightmapOffset", glm.vec2(obj["lightmapUVOffset"][0], obj["lightmapUVOffset"][1]))

            subMesh.bind()
            glDrawElements(GL_TRIANGLES, subMesh.indicesAmount, GL_UNSIGNED_INT, None )
            subMesh.unbind()


    #Gather the interpolated data from the render passes
    lightmapsData = {}
    for obj in scene["sceneObjects"]:
        lightmapTexName = obj["lightmapTexName"]
        lightmapSize = obj["lightmapSize"]

        glBindFramebuffer(GL_FRAMEBUFFER, lightmapsFrameBuffers[lightmapTexName][2])

        #read from position color attachment
        glReadBuffer(GL_COLOR_ATTACHMENT0)
        format32f = formats["RGB32F"]
        data = glReadPixels(0, 0, lightmapSize, lightmapSize, format32f["format"], format32f["type"])
        posData32f = np.frombuffer(data, dtype = format32f["npType"]).reshape(lightmapSize, lightmapSize, 3)

        #read from normals color attachment
        glReadBuffer(GL_COLOR_ATTACHMENT1)
        format8ui = formats["RGB32F"]
        data = glReadPixels(0, 0, lightmapSize, lightmapSize, format8ui["format"], format8ui["type"])
        normalData8 = np.frombuffer(data, dtype=format8ui["npType"]).reshape(lightmapSize, lightmapSize, 3)

        #read from object id color attachment
        glReadBuffer(GL_COLOR_ATTACHMENT2)
        format32ui = formats["RGB32UI"]
        data = glReadPixels(0, 0, lightmapSize, lightmapSize, format32ui["format"], format32ui["type"])
        objIdData32ui = np.frombuffer(data, dtype = format32ui["npType"]).reshape(lightmapSize, lightmapSize, 3)
        
        interpData = {
            "pos": posData32f,
            "normal": normalData8,
            "objId": objIdData32ui,
            "texSize": lightmapSize,
        }
        
        lightmapsData[lightmapTexName] = interpData

    #Clean UV raster opengl resources
    for lightmapTexName in lightmapsFrameBuffers:
        lightmapFBO =  lightmapsFrameBuffers[lightmapTexName]
        glDeleteFramebuffers(1, [lightmapFBO[2]])
        glDeleteTextures(3, lightmapFBO[0])
        glDeleteRenderbuffers(1, [lightmapFBO[1]])
    
    glDeleteProgram(shaderRasterPos)
    return lightmapsData

"""
Creates a dict with all of the scene info from the scene json, it also creates a vbo for each mesh and calculates its transform matrix.
"""
def getSceneInformation(resourcesPath, sceneFilePath):

    meshes = {}
    sceneLights = []
    sceneObjects = []

    with open(sceneFilePath, 'r') as file:
        sceneJson = json.load(file)
        for obj in sceneJson["objects"]:
            meshPath = obj["mesh"]
            if meshPath not in meshes:
                with open(resourcesPath + meshPath, 'r') as file: 
                    meshJson = json.load(file)

                    me = Mesh()
                    me.name = meshPath
                    
                    for mesh in meshJson["meshes"]:
                        verticesArray = base64ToFloatArray (mesh["vertices"])
                        indicesArray = base64ToUint32Array (mesh["indices"])
                        meshBuffer = OpenglMeshBuffer(verticesArray, indicesArray)
                        me.subMeshes.append(meshBuffer)

                    meshes[meshPath] = me

            posMat = glm.translate(glm.mat4(1.0), glm.vec3(obj["position"][0], obj["position"][1], obj["position"][2]))  
            rotMat = eulerToMat4(obj["rotation"][0], obj["rotation"][1], obj["rotation"][2])
            scaleMat = glm.scale(glm.mat4(1.0), glm.vec3(obj["scale"][0], obj["scale"][1], obj["scale"][2]))
            
            transform = posMat * rotMat * scaleMat
            obj["transform"] = transform
            obj["rotMat"] = rotMat

            sceneObjects.append(obj)
        
        for light in sceneJson["lights"]:
            meshPath = light["mesh"]

            if meshPath not in meshes:
                with open(resourcesPath + meshPath, 'r') as file: 
                    meshJson = json.load(file)

                    me = Mesh()
                    me.name = meshPath
                    
                    for mesh in meshJson["meshes"]:
                        verticesArray = base64ToFloatArray( mesh["vertices"] )
                        indicesArray = base64ToUint32Array( mesh["indices"] )
                        meshBuffer = OpenglMeshBuffer( verticesArray, indicesArray )
                        me.subMeshes.append(meshBuffer)

                    meshes[meshPath] = me
                
            posMat = glm.translate(glm.mat4(1.0), glm.vec3(light["position"][0], light["position"][1], light["position"][2]))  
            rotMat = eulerToMat4(light["rotation"][0], light["rotation"][1], light["rotation"][2])
            scaleMat = glm.scale(glm.mat4(1.0), glm.vec3(light["scale"][0], light["scale"][1], light["scale"][2]))

            transform = posMat * rotMat * scaleMat
            light["transform"] = transform
            light["rotMat"] = rotMat

            sceneLights.append(light)

    return {"meshes": meshes, "sceneObjects": sceneObjects, "lights": sceneLights}

def savePng(path, imageArray, format = "RGBA"):
    image = Image.fromarray(imageArray , format)
    image = np.flip(image, axis=0)
    img = Image.fromarray(image)
    img.save(path + ".png")
    print("---- .png saved to: " + path + ".png")

def saveExr(path, imageArray):
    imageArray = np.flip(imageArray, axis=0)
    pyexr.write(path+".exr", imageArray)
    print("---- .exr saved to: " + path + ".exr")