import pygame
from pygame.locals import *
from OpenGL.GL import *
import json
import numpy as np
import glm
from openGLutils import *
from utils import *
import time
from shaders import *
import os

resources_path = "D:\\Users\\Felipe\\Desktop\\TestRaytracingScene\\New\\"
#resources_path = "D:\\Users\\Felipe\\Desktop\\Proyectos\\MyTinyGameEngine\\MySimpleGE-Samples\\resources\\"
output_path = "D:\\Users\\Felipe\\Desktop\\TestRaytracingScene\\New\\"

def create_renderPassTexture(tex_size):
    #RENDER TEXTURE
    pos_texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, pos_texture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB32F, tex_size, tex_size, 0, GL_RGB, GL_FLOAT, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glBindTexture(GL_TEXTURE_2D, 0)

    normal_texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, normal_texture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB32F, tex_size, tex_size, 0, GL_RGB, GL_FLOAT, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glBindTexture(GL_TEXTURE_2D, 0)

    id_texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, id_texture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB32UI, tex_size, tex_size, 0, GL_RGB_INTEGER, GL_UNSIGNED_INT, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glBindTexture(GL_TEXTURE_2D, 0)
    
    #DEPTH BUFFER
    depth_buffer = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, depth_buffer)
    # Create the depth buffer's storage
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, tex_size, tex_size)
   
    #FRAME BUFFER
    fbo = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, fbo);  

    #ATTACH COLOR
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, pos_texture, 0)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT1, GL_TEXTURE_2D, normal_texture, 0)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT2, GL_TEXTURE_2D, id_texture, 0)
    
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, depth_buffer)

    attachments = [GL_COLOR_ATTACHMENT0,GL_COLOR_ATTACHMENT1,GL_COLOR_ATTACHMENT2]
    glDrawBuffers(3, attachments)

    if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        check_framebuffer_status()
        return (0,0,0)
    
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    glBindRenderbuffer(GL_RENDERBUFFER, 0)
    return ([pos_texture, normal_texture, id_texture], depth_buffer, fbo)

def createMultiplierCubeMesh():
    
    vertices = "AACAvwAAgD8AAIC/AACAPwAAAAAAAAAAAAAAAAAAAAAAAAAAAADAPgAAgD4AAIC/AACAvwAAgD8AAIA/AAAAAAAAAAAAAAAAAAAAAAAAAAAAACA/AAAAAAAAgL8AAIC/AACAvwAAgD8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAwD4AAAAAAACAPwAAgD8AAIC/AAAAAAAAgL8AAAAAAAAAAAAAAAAAAAAAAADAPgAAAD8AAIC/AACAPwAAgD8AAAAAAACAvwAAAAAAAAAAAAAAAAAAAAAAACA/AACAPgAAgL8AAIA/AACAvwAAAAAAAIC/AAAAAAAAAAAAAAAAAAAAAAAAwD4AAIA+AACAPwAAgL8AAIC/AACAvwAAAAAAAAAAAAAAAAAAAAAAAAAAAADAPgAAQD8AAIA/AACAPwAAgD8AAIC/AAAAAAAAAAAAAAAAAAAAAAAAAAAAACA/AAAAPwAAgD8AAIA/AACAvwAAgL8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAwD4AAAA/AACAvwAAgL8AAIC/AAAAAAAAgD8AAAAAAAAAAAAAAAAAAAAAAADAPgAAgD8AAIA/AACAvwAAgD8AAAAAAACAPwAAAAAAAAAAAAAAAAAAAAAAACA/AABAPwAAgD8AAIC/AACAvwAAAAAAAIA/AAAAAAAAAAAAAAAAAAAAAAAAwD4AAEA/AACAvwAAgL8AAIC/AAAAAAAAAAAAAIA/AAAAAAAAAAAAAAAAAAAAPgAAQD8AAIA/AACAPwAAgL8AAAAAAAAAAAAAgD8AAAAAAAAAAAAAAAAAAMA+AAAAPwAAgL8AAIA/AACAvwAAAAAAAAAAAACAPwAAAAAAAAAAAAAAAAAAAD4AAAA/AACAPwAAgL8AAIA/AAAAAAAAAAAAAIC/AAAAAAAAAAAAAAAAAAAgPwAAQD8AAIC/AACAPwAAgD8AAAAAAAAAAAAAgL8AAAAAAAAAAAAAAAAAAGA/AAAAPwAAgD8AAIA/AACAPwAAAAAAAAAAAACAvwAAAAAAAAAAAAAAAAAAID8AAAA/AACAvwAAgD8AAIC/AACAPwAAAAAAAAAAAAAAAAAAAAAAAAAAAADAPgAAgD4AAIC/AACAPwAAgD8AAIA/AAAAAAAAAAAAAAAAAAAAAAAAAAAAACA/AACAPgAAgL8AAIC/AACAPwAAgD8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAID8AAAAAAACAPwAAgD8AAIC/AAAAAAAAgL8AAAAAAAAAAAAAAAAAAAAAAADAPgAAAD8AAIA/AACAPwAAgD8AAAAAAACAvwAAAAAAAAAAAAAAAAAAAAAAACA/AAAAPwAAgL8AAIA/AACAPwAAAAAAAIC/AAAAAAAAAAAAAAAAAAAAAAAAID8AAIA+AACAPwAAgL8AAIC/AACAvwAAAAAAAAAAAAAAAAAAAAAAAAAAAADAPgAAQD8AAIA/AACAvwAAgD8AAIC/AAAAAAAAAAAAAAAAAAAAAAAAAAAAACA/AABAPwAAgD8AAIA/AACAPwAAgL8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAID8AAAA/AACAvwAAgL8AAIC/AAAAAAAAgD8AAAAAAAAAAAAAAAAAAAAAAADAPgAAgD8AAIC/AACAvwAAgD8AAAAAAACAPwAAAAAAAAAAAAAAAAAAAAAAACA/AACAPwAAgD8AAIC/AACAPwAAAAAAAIA/AAAAAAAAAAAAAAAAAAAAAAAAID8AAEA/AACAvwAAgL8AAIC/AAAAAAAAAAAAAIA/AAAAAAAAAAAAAAAAAAAAPgAAQD8AAIA/AACAvwAAgL8AAAAAAAAAAAAAgD8AAAAAAAAAAAAAAAAAAMA+AABAPwAAgD8AAIA/AACAvwAAAAAAAAAAAACAPwAAAAAAAAAAAAAAAAAAwD4AAAA/AACAPwAAgL8AAIA/AAAAAAAAAAAAAIC/AAAAAAAAAAAAAAAAAAAgPwAAQD8AAIC/AACAvwAAgD8AAAAAAAAAAAAAgL8AAAAAAAAAAAAAAAAAAGA/AABAPwAAgL8AAIA/AACAPwAAAAAAAAAAAACAvwAAAAAAAAAAAAAAAAAAYD8AAAA/"
    indices = "AAAAAAEAAAACAAAAAwAAAAQAAAAFAAAABgAAAAcAAAAIAAAACQAAAAoAAAALAAAADAAAAA0AAAAOAAAADwAAABAAAAARAAAAEgAAABMAAAAUAAAAFQAAABYAAAAXAAAAGAAAABkAAAAaAAAAGwAAABwAAAAdAAAAHgAAAB8AAAAgAAAAIQAAACIAAAAjAAAA"
    vertices_array = base64_to_float_array (vertices)
    indices_array = base64_to_uint32_array (indices)

    meshBuffer = OpenglMeshBuffer(vertices_array, indices_array)

    multiplierCubeMesh = Mesh()
    multiplierCubeMesh.sub_meshes.append(meshBuffer)

    return multiplierCubeMesh

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

def renderHemisphereScene(scene, shader, fbo, fboRenderSize, onlyRenderMultiplier, renderLight, cameraPos : glm.vec3, cameraForward : glm.vec3, cameraUp : glm.vec3):
    near_plane = 0.001
    far_plane = 100.0

    cubemapProj = glm.perspective(glm.radians(90.0), 1.0, near_plane, far_plane)
    cameraMat = glm.orientation( cameraForward , cameraUp)
    cameraMat = glm.mat3(cameraMat)

    cubemapTransforms = []
    cubemapTransforms.append(glm.lookAt( cameraPos , cameraPos + cameraMat * glm.vec3(1.0, 0.0, 0.0), cameraMat * glm.vec3(0.0, -1.0, 0.0) ) )
    cubemapTransforms.append(glm.lookAt( cameraPos , cameraPos + cameraMat * glm.vec3(-1.0, 0.0, 0.0), cameraMat * glm.vec3(0.0, -1.0, 0.0) ) )
    cubemapTransforms.append(glm.lookAt( cameraPos , cameraPos + cameraMat * glm.vec3(0.0, 1.0, 0.0), cameraMat * glm.vec3(0.0, 0.0, 1.0) ) )
    cubemapTransforms.append(glm.lookAt( cameraPos , cameraPos + cameraMat * glm.vec3(0.0, -1.0, 0.0), cameraMat * glm.vec3(0.0, 0.0, -1.0) ) )
    cubemapTransforms.append(glm.lookAt( cameraPos , cameraPos + cameraMat * glm.vec3(0.0, 0.0, 1.0), cameraMat * glm.vec3(0.0, -1.0, 0.0) ) )
    cubemapTransforms.append(glm.lookAt( cameraPos , cameraPos + cameraMat * glm.vec3(0.0, 0.0, -1.0), cameraMat * glm.vec3(0.0, -1.0, 0.0) ) )

    for idx in range(6):
        set_uniform_matrix(shader, "cubemapSidesMatrices[" + str(idx) + "]",  cubemapTransforms[idx])
    
    
    set_uniform_vec3(shader, "color", glm.vec3(1.0,1.0,1.0))
    set_uniform_vec3(shader, "cameraUp", cameraUp)
    set_uniform_vec3(shader, "cameraPos", cameraPos)
    set_uniform_matrix(shader, "projMat", cubemapProj)
    set_uniform_float (shader, "texResolution", fboRenderSize)

    #glActiveTexture(GL_TEXTURE0) 
    #glBindTexture(GL_TEXTURE_2D, scene["textures"]["concrete"].texture_id)
    #glUniform1i(glGetUniformLocation(shader, "tex1"), 0)
    
    #set_uniform_matrix(shader, "viewMat" , cubemapTransforms[idx])
        
    #glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_CUBE_MAP_POSITIVE_X+0, fbo[0], 0)
    #glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_CUBE_MAP_POSITIVE_X+0, fbo[1], 0)

    glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, fbo[0], 0)
    glFramebufferTexture(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, fbo[1], 0)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  

    for obj in scene["objects_to_render"]:
        mesh_name = obj["mesh"]
        mesh_to_render = scene["meshes"][mesh_name]
        lightmapName = obj["lightmapTexName"]
        
        # Deal with lightmaps
        if lightmapName in scene["lightmaps"]:
            lightmapTex = scene["lightmaps"][lightmapName]["openglTex"]
            glActiveTexture(GL_TEXTURE1) 
            glBindTexture(GL_TEXTURE_2D, lightmapTex.texture_id)
            glUniform1i(glGetUniformLocation(shader, "lightmap"), 1)
        else:
            glActiveTexture(GL_TEXTURE1) 
            glBindTexture(GL_TEXTURE_2D, 0)
            glUniform1i(glGetUniformLocation(shader, "lightmap"), 1)

        for sub_mesh in mesh_to_render.sub_meshes:
            
            set_uniform_matrix(shader, "modelMat", obj["transform"])
            set_uniform_vec2(shader, "lightmapTiling", glm.vec2(obj["lightmapUVTiling"][0], obj["lightmapUVTiling"][1]))
            set_uniform_vec2(shader, "lightmapOffset", glm.vec2(obj["lightmapUVOffset"][0], obj["lightmapUVOffset"][1]))
            set_uniform_int(shader, "isLight", 0)

            if onlyRenderMultiplier:
                set_uniform_int(shader, "isLight", 2)

            sub_mesh.bind()
            glDrawElements(GL_TRIANGLES, sub_mesh.indices_amount, GL_UNSIGNED_INT, None )
            sub_mesh.unbind()

    if renderLight:
        for light in scene["lights"]:
            mesh_name = light["mesh"]
            mesh_to_render = scene["meshes"][mesh_name]

            for sub_mesh in mesh_to_render.sub_meshes:
                
                set_uniform_matrix(shader, "modelMat", light["transform"])
                set_uniform_int(shader, "isLight", 1)
                set_uniform_vec3(shader, "color", light["color"])
                set_uniform_float(shader, "lightIntensity", light["intensity"])

                if onlyRenderMultiplier:
                    set_uniform_int(shader, "isLight", 2)

                sub_mesh.bind()
                glDrawElements(GL_TRIANGLES, sub_mesh.indices_amount, GL_UNSIGNED_INT, None )
                sub_mesh.unbind()
    
def calculateTexelLightValue(cubemapFBO, multiplerCompensationValue, fboRenderSize = 256):
    #glBindFramebuffer(GL_FRAMEBUFFER, cubemapFBO[2])
    
    #read from position color attachment
    #glReadBuffer(GL_COLOR_ATTACHMENT0)

    colorValue = glm.vec3(0.0,0.0,0.0)

    for idx in range(6):
        
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_CUBE_MAP_POSITIVE_X+idx, cubemapFBO[0], 0)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_CUBE_MAP_POSITIVE_X+idx, cubemapFBO[1], 0)

        data = glReadPixels(0, 0, fboRenderSize, fboRenderSize, formats["RGBA16F"]["format"], formats["RGBA16F"]["type"])
        cubemapColorData = np.frombuffer(data, dtype = formats["RGBA16F"]["npType"]).reshape(fboRenderSize, fboRenderSize, 4)

        accumulation = cubemapColorData.sum(axis=(0, 1)) 
        colorValue += glm.vec3(accumulation[0], accumulation[1], accumulation[2])
        """
        for pixI in range(fboRenderSize):
            for pixJ in range(fboRenderSize):
                if cubemapColorData[pixI][pixJ][3] > 0.0:
                    colorValue += glm.vec3(cubemapColorData[pixI][pixJ][0], cubemapColorData[pixI][pixJ][1], cubemapColorData[pixI][pixJ][2])
        """
    colorValue /= multiplerCompensationValue

    return colorValue

def calculateMultiplierUniform(cubemapFBO, fboRenderSize = 256):
    
    #glBindFramebuffer(GL_FRAMEBUFFER, cubemapFBO[2])
    
    #read from position color attachment
    #glReadBuffer(GL_COLOR_ATTACHMENT0)

    value = 0.0
    for idx in range(6):
        
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_CUBE_MAP_POSITIVE_X+idx, cubemapFBO[0], 0)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_CUBE_MAP_POSITIVE_X+idx, cubemapFBO[1], 0)

        data = glReadPixels(0, 0, fboRenderSize, fboRenderSize, formats["RGBA16F"]["format"], formats["RGBA16F"]["type"])
        cubemapColorData = np.frombuffer(data, dtype = formats["RGBA16F"]["npType"]).reshape(fboRenderSize, fboRenderSize, 4)

        for pixI in range(fboRenderSize):
            for pixJ in range(fboRenderSize):
                if cubemapColorData[pixI][pixJ][3] > 0.0:
                    value += cubemapColorData[pixI][pixJ][0]

    return value       
 
def radiosityRender(scene, interp_data, fboRenderSize = 256):
    shaderCubeMapRender = create_shader_program_w_geometry(cubemap_vshader, cubemap_fshader, cubemap_gshader)
    glViewport(0, 0, fboRenderSize, fboRenderSize)
    cubemapFBO = createCubeMapFBO(fboRenderSize)
    #Only for test fbo 
    #snapshotFBO = createCubeMapFBO(512)


    # Load image using Pillow
    #image = Image.open(resources_path + "concretewall022a.png")
    #image = image.convert("RGB")
    #image_data = image.transpose(Image.FLIP_TOP_BOTTOM).tobytes() 
    #img_data = np.array(image, dtype=np.uint8)
    #concreteTexture = OpenGLTexture(image.width, image.height, formats["default"], image_data)
    
    #textures = {
    #    "concrete" : concreteTexture
    #}
    #scene["textures"] = textures
    scene["lightmaps"] = {}

    #---------- Multiplier Calculation

    glUseProgram(shaderCubeMapRender)
    glBindFramebuffer(GL_FRAMEBUFFER, cubemapFBO[2])
    glDrawBuffer(GL_COLOR_ATTACHMENT0)

    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE) 

    glReadBuffer(GL_COLOR_ATTACHMENT0)

    multiplierCubeScene = {
        'meshes': {'multiplierCube': createMultiplierCubeMesh()},
        'objects_to_render': [{'mesh': 'multiplierCube', 
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
        'lightmaps': {}
    }
    renderHemisphereScene(multiplierCubeScene, shaderCubeMapRender, cubemapFBO, fboRenderSize, True, False, glm.vec3(0.0,0.0,0.0), glm.vec3(0.0,1.0,0.0), glm.vec3(0.0,0.0,1.0))
    multiplerCompensationValue = calculateMultiplierUniform(cubemapFBO, fboRenderSize)
    
    print ("Multiplier Compensation: " + str(multiplerCompensationValue))


    #-----Normal Render 
    for iterations in range(6):
        #update or create lightmap textures previous each iteration:
       
        for lightmapTexName in interp_data:
            if lightmapTexName not in scene["lightmaps"]:
                render_tex_size = interp_data[lightmapTexName]["texSize"]
                imgData = np.zeros((render_tex_size, render_tex_size, 3), dtype= np.float32)
                CurrentLightmapTex = {
                    "data": imgData,
                    "openglTex": OpenGLTexture(render_tex_size, render_tex_size, formats["RGB32F"], imgData)
                }
                scene["lightmaps"][lightmapTexName] = CurrentLightmapTex

            else:
                CurrentLightmapTex = scene["lightmaps"][lightmapTexName]
                imgData = CurrentLightmapTex["data"]
                openglTex = CurrentLightmapTex["openglTex"]
                openglTex.update(imgData, GL_TEXTURE1)

        
        glUseProgram(shaderCubeMapRender)
        glBindFramebuffer(GL_FRAMEBUFFER, cubemapFBO[2])
        glDrawBuffer(GL_COLOR_ATTACHMENT0)

        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE) 

        glReadBuffer(GL_COLOR_ATTACHMENT0)
   
        for lightmapTexName in interp_data:

            interp_pos = interp_data[lightmapTexName]["pos"]  
            interp_normal = interp_data[lightmapTexName]["normal"]
            objects_id = interp_data[lightmapTexName]["objId"] 
            render_tex_size = interp_data[lightmapTexName]["texSize"]
            
            imgData = scene["lightmaps"][lightmapTexName]["data"]

            for pixI in range(render_tex_size):
                print ("Progress line: " + str(pixI) )
                for pixJ in range(render_tex_size):

                    pixelPosition = glm.vec3(interp_pos[pixI][pixJ])
                    pixelNormal = glm.vec3(interp_normal[pixI][pixJ])
                    pixelId = objects_id[pixI][pixJ]

                    if pixelId[0] > 0.05:

                        cameraForward = glm.vec3(1.0,0.0,0.0)
                        
                        dotProdValue = glm.dot(cameraForward, glm.normalize(pixelNormal))
                        if abs(dotProdValue) >= 0.999:
                            cameraForward = glm.vec3(0.0,1.0,0.0)

                        cameraForward = glm.cross(cameraForward,  glm.normalize(pixelNormal))    

                        renderHemisphereScene(scene, 
                            shaderCubeMapRender,
                            cubemapFBO,
                            fboRenderSize,
                            False,
                            True,
                            pixelPosition,
                            cameraForward,
                            glm.normalize(pixelNormal)
                            )
                        
                        finalColorValue = calculateTexelLightValue(cubemapFBO, multiplerCompensationValue, fboRenderSize)

                        finalPixel = np.array([finalColorValue.r, finalColorValue.g, finalColorValue.b])# * 255
                        imgData[pixI][pixJ] = finalPixel

            #save_renderTexture_to_disk(resources_path + "radiosityRender" + lightmapTexName, render_tex_size, render_tex_size, finalRender, "RGBA")

        if (iterations+1) % 1 == 0:
            for lightmapTexName in interp_data:
                render_tex_size = interp_data[lightmapTexName]["texSize"]
                imgData = scene["lightmaps"][lightmapTexName]["data"]

                scaled_array = imgData * 255.0
                scaled_array = np.clip(scaled_array, 0, 255)
                uint8_array = scaled_array.astype(np.uint8)

                file_name = os.path.basename(lightmapTexName)

                save_renderTexture_to_disk(output_path + "radiosityRender" + file_name + str(iterations), render_tex_size, render_tex_size, uint8_array, "RGB")

def main():
    pygame.init()

    render_tex_size = 128
    display = (render_tex_size, render_tex_size)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    
    meshes = {}
    sceneLights = []
    objects_to_render = []
    renderTextures = {}
    scene_path = "Scene1.json"
    #scene_path = "SampleScene.json"

    with open(resources_path + scene_path, 'r') as file:
        scene_json = json.load(file)
        for obj in scene_json["objects"]:
            mesh_path = obj["mesh"]
            if mesh_path not in meshes:
                with open(resources_path + mesh_path, 'r') as file: 
                    mesh_json = json.load(file)

                    me = Mesh()
                    me.name = mesh_path
                    
                    for mesh in mesh_json["meshes"]:
                        vertices_array = base64_to_float_array (mesh["vertices"])
                        indices_array = base64_to_uint32_array (mesh["indices"])
                        meshBuffer = OpenglMeshBuffer(vertices_array, indices_array)
                        me.sub_meshes.append(meshBuffer)

                    meshes[mesh_path] = me
            
            lightmapName = obj["lightmapTexName"]
            if lightmapName not in renderTextures:
                renderTextures[lightmapName] = create_renderPassTexture(render_tex_size)

            pos_mat = glm.translate(glm.mat4(1.0), glm.vec3(obj["position"][0], obj["position"][1], obj["position"][2]))  
            rot_mat = euler_to_mat4(obj["rotation"][0], obj["rotation"][1], obj["rotation"][2])
            scale_mat = glm.scale(glm.mat4(1.0), glm.vec3(obj["scale"][0], obj["scale"][1], obj["scale"][2]))
            
            transform = pos_mat * rot_mat * scale_mat
            obj["transform"] = transform
            obj["rot_mat"] = rot_mat

            objects_to_render.append(obj)
        
        for light in scene_json["lights"]:
            mesh_path = light["mesh"]

            if mesh_path not in meshes:
                with open(resources_path + mesh_path, 'r') as file: 
                    mesh_json = json.load(file)

                    me = Mesh()
                    me.name = mesh_path
                    
                    for mesh in mesh_json["meshes"]:
                        vertices_array = base64_to_float_array (mesh["vertices"])
                        indices_array = base64_to_uint32_array (mesh["indices"])
                        meshBuffer = OpenglMeshBuffer(vertices_array, indices_array)
                        me.sub_meshes.append(meshBuffer)

                    meshes[mesh_path] = me
                
            pos_mat = glm.translate(glm.mat4(1.0), glm.vec3(light["position"][0], light["position"][1], light["position"][2]))  
            rot_mat = euler_to_mat4(light["rotation"][0], light["rotation"][1], light["rotation"][2])
            scale_mat = glm.scale(glm.mat4(1.0), glm.vec3(light["scale"][0], light["scale"][1], light["scale"][2]))

            transform = pos_mat * rot_mat * scale_mat
            light["transform"] = transform
            light["rot_mat"] = rot_mat
            light["color"] = glm.vec3(light["color"][0], light["color"][1], light["color"][2])

            sceneLights.append(light)
                    

    #Rasterize into UV space stage-----------------------
    # Initialize OpenGL settings
    glViewport(0, 0, display[0], display[1])
    glClearColor(0.0, 0.0, 0.0, 1.0)
    #glEnable(GL_DEPTH_TEST)
    #glEnable(GL_CULL_FACE)

    # Compile shaders and create program

    shader_RasterPos = create_shader_program(uv_raster_vshader, uv_raster_fshader)
    
    near_plane = 0.01
    far_plane = 50.0

    glViewport(0, 0, display[0], display[1])

    #RENDER pos,normal,id
    glUseProgram(shader_RasterPos) 
    glDisable(GL_BLEND) 
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE)
    #glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)          

    i = 1
    for obj in objects_to_render:
        mesh_name = obj["mesh"]
        mesh_to_render = meshes[mesh_name]

        lightmapTexName = obj["lightmapTexName"]
        rt = renderTextures[lightmapTexName]

        glBindFramebuffer(GL_FRAMEBUFFER, rt[2])

        j = 1
        #ZUpMatrix *
        for sub_mesh in mesh_to_render.sub_meshes:
            set_uniform_matrix(shader_RasterPos, "modelMat", obj["transform"])
            set_uniform_matrix(shader_RasterPos, "viewMat", glm.mat4(1.0))
            set_uniform_matrix(shader_RasterPos, "projMat", glm.perspective(90.0, 1.0, 0.01, 1000.0))

            set_uniform_uvec2(shader_RasterPos, "objId", glm.uvec2(i,j))  
            set_uniform_vec2(shader_RasterPos, "lightmapTiling", glm.vec2(obj["lightmapUVTiling"][0], obj["lightmapUVTiling"][1]))
            set_uniform_vec2(shader_RasterPos, "lightmapOffset", glm.vec2(obj["lightmapUVOffset"][0], obj["lightmapUVOffset"][1]))

            sub_mesh.bind()
            glDrawElements(GL_TRIANGLES, sub_mesh.indices_amount, GL_UNSIGNED_INT, None )
            sub_mesh.unbind()

            j += 1
        i += 1


    #Gather the interpolated data from the render passes
    lightmaps_interpolated_data = {}
    i = 0
    for lightmapTexName in renderTextures:
        glBindFramebuffer(GL_FRAMEBUFFER, renderTextures[lightmapTexName][2])

        #read from position color attachment
        glReadBuffer(GL_COLOR_ATTACHMENT0)
        format32f = formats["RGB32F"]
        data = glReadPixels(0, 0, render_tex_size, render_tex_size, format32f["format"], format32f["type"])
        posData32f = np.frombuffer(data, dtype = format32f["npType"]).reshape(render_tex_size, render_tex_size, 3)

        #read from normals color attachment
        glReadBuffer(GL_COLOR_ATTACHMENT1)
        format8ui = formats["RGB32F"]
        data = glReadPixels(0, 0, render_tex_size, render_tex_size, format8ui["format"], format8ui["type"])
        normalData8 = np.frombuffer(data, dtype=format8ui["npType"]).reshape(render_tex_size, render_tex_size, 3)

        #read from object id color attachment
        glReadBuffer(GL_COLOR_ATTACHMENT2)
        format32ui = formats["RGB32UI"]
        data = glReadPixels(0, 0, render_tex_size, render_tex_size, format32ui["format"], format32ui["type"])
        objIdData32ui = np.frombuffer(data, dtype = format32ui["npType"]).reshape(render_tex_size, render_tex_size, 3)
        
        interp_data = {
            "pos": posData32f,
            "normal": normalData8,
            "objId": objIdData32ui,
            "texSize": render_tex_size,
        }
        
        lightmaps_interpolated_data[lightmapTexName] = interp_data

        i += 1


    radiosityRender({"meshes": meshes, "objects_to_render": objects_to_render, "lights": sceneLights}, lightmaps_interpolated_data, 128)

    pygame.display.flip()
    
    # Main loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()


        #pygame.time.wait(10)

if __name__ == "__main__":
    main()