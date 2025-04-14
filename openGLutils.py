from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import glm
import numpy as np

max_float32 = 3.402823466e+38
min_float32 = -3.402823466e+38

formats = {
    "default" : 
    {
        "internalformat":GL_RGB,
        "format":GL_RGB,
        "type":GL_UNSIGNED_BYTE,
        "npType":np.uint8
    },

    "RGB32UI" : 
    {
        "internalformat":GL_RGB32UI,
        "format":GL_RGB_INTEGER,
        "type": GL_UNSIGNED_INT,
        "npType": np.uint32
    },
    "RGB32F" : 
    {
        "internalformat":GL_RGB32F,
        "format":GL_RGB,
        "type": GL_FLOAT,
        "npType": np.float32
    },
    "RGBA16F" : 
    {
        "internalformat":GL_RGBA16F,
        "format":GL_RGBA,
        "type": GL_FLOAT,
        "npType": np.float32
    },
}

def check_opengl_error():
    error = glGetError()
    if error != GL_NO_ERROR:
        if error == GL_INVALID_ENUM:
            print("OpenGL Error: GL_INVALID_ENUM")
        elif error == GL_INVALID_VALUE:
            print("OpenGL Error: GL_INVALID_VALUE")
        elif error == GL_INVALID_OPERATION:
            print("OpenGL Error: GL_INVALID_OPERATION")
        elif error == GL_STACK_OVERFLOW:
            print("OpenGL Error: GL_STACK_OVERFLOW")
        elif error == GL_STACK_UNDERFLOW:
            print("OpenGL Error: GL_STACK_UNDERFLOW")
        elif error == GL_OUT_OF_MEMORY:
            print("OpenGL Error: GL_OUT_OF_MEMORY")
        else:
            print(f"OpenGL Error: {error}")

def check_framebuffer_status():
    status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
    if status == GL_FRAMEBUFFER_COMPLETE:
        print("Framebuffer is complete!")
    elif status == GL_FRAMEBUFFER_UNDEFINED:
        print("Framebuffer undefined!")
    elif status == GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT:
        print("Framebuffer incomplete: Incomplete attachment!")
    elif status == GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT:
        print("Framebuffer incomplete: Missing attachment!")
    elif status == GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER:
        print("Framebuffer incomplete: Draw buffer!")
    elif status == GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER:
        print("Framebuffer incomplete: Read buffer!")
    elif status == GL_FRAMEBUFFER_UNSUPPORTED:
        print("Framebuffer incomplete: Unsupported format!")
    elif status == GL_FRAMEBUFFER_INCOMPLETE_MULTISAMPLE:
        print("Framebuffer incomplete: Multisample issue!")
    elif status == GL_FRAMEBUFFER_INCOMPLETE_LAYER_TARGETS:
        print("Framebuffer incomplete: Layer targets issue!")
    else:
        print(f"Framebuffer incomplete: Unknown error, status code: {status}")

def create_frameBuffer(format):
    #RENDER TEXTURE
    rendered_texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, rendered_texture)

    glTexImage2D(GL_TEXTURE_2D, 0, format["internalformat"], 1024, 1024, 0, format["format"], format["type"], None)
    # Set texture filtering
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
   
    
    #DEPTH BUFFER
    depth_buffer = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, depth_buffer)
    # Create the depth buffer's storage
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, 1024, 1024)
   
    #FRAME BUFFER
    fbo = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, fbo);  

    #ATTACH COLOR
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, rendered_texture, 0)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, depth_buffer)

    if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        check_framebuffer_status()
        return (0,0,0)
    
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    glBindRenderbuffer(GL_RENDERBUFFER, 0)
    glBindTexture(GL_TEXTURE_2D, 0)

    return (rendered_texture, depth_buffer, fbo)

# Function to set a mat4 uniform
def set_uniform_matrix(program, name, matrix):
    location = glGetUniformLocation(program, name)
    glUniformMatrix4fv(location, 1, GL_FALSE, glm.value_ptr(matrix))


def set_uniform_vec2(program, name, value):
    location = glGetUniformLocation(program, name)
    glUniform2fv(location, 1, glm.value_ptr(value))
    
def set_uniform_vec3(program, name, value):
    location = glGetUniformLocation(program, name)
    glUniform3fv(location, 1, glm.value_ptr(value))

def set_uniform_float(program, name, value):
    location = glGetUniformLocation(program, name)
    glUniform1f(location, value)

def set_uniform_uvec2(program, name, value):
    location = glGetUniformLocation(program, name)
    glUniform2uiv(location, 1, glm.value_ptr(value))

def set_uniform_int(program, name, value):
    location = glGetUniformLocation(program, name)
    glUniform1i(location, value)

class OpenglMeshBuffer:
    def __init__(self, vertices: np.ndarray, indices: np.ndarray):
        self.VBO = -1
        self.VAO = -1
        self.IBO = -1
        self.indices_amount = 0

        self.vertices = vertices
        self.indices = indices
        
        if vertices.dtype == np.float32 and indices.dtype == np.uint32:
            
            self.VAO = glGenVertexArrays(1)
            self.IBO = glGenBuffers(1)
            self.VBO = glGenBuffers(1)
            
            glBindVertexArray(self.VAO)

            # Fill the buffer with the vertex data
            glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
            glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.IBO)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
            self.indices_amount = indices.size

            position_size = 3  
            normal_size = 3 
            color = 3    
            uv1_size = 2  

            stride = (position_size + normal_size + color + uv1_size) * vertices.itemsize

            #Link vertex attributes
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)

            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(position_size * vertices.itemsize))
            glEnableVertexAttribArray(1)

            glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p((position_size + normal_size) * vertices.itemsize))
            glEnableVertexAttribArray(2)

            glVertexAttribPointer(3, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p((position_size + normal_size + color) * vertices.itemsize))
            glEnableVertexAttribArray(3)

            self.unbind()

    def bind(self):
        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.IBO)

    def unbind(self):
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0) 

class Mesh:
    def __init__(self):
        self.name = ""
        self.sub_meshes = []
    

class OpenGLTexture:
    def __init__(self, width, height, format, pixels: np.ndarray):
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        self.width = width
        self.height = height
        self.format = format

        glTexImage2D(GL_TEXTURE_2D, 0, format["internalformat"], self.width, self.height , 0, format["format"], format["type"], pixels)
        glGenerateMipmap(GL_TEXTURE_2D)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);	
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

    def bind(self):
        #Bind the texture for rendering.
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

    def unbind(self):
        #Unbind the texture.
        glBindTexture(GL_TEXTURE_2D, 0)

    def update(self, newImageData, texSlot):
        glActiveTexture(texSlot) 
        self.bind()
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, self.width, self.height, self.format["format"], self.format["type"], newImageData)
        self.unbind()

    def __del__(self):
        #Delete the texture when the object is destroyed.
        self.unbind()
        glDeleteTextures(1, [self.texture_id])


def create_shader_program(vertex_source: str, fragment_source: str):
    program = compileProgram(
        compileShader(vertex_source, GL_VERTEX_SHADER),
        compileShader(fragment_source, GL_FRAGMENT_SHADER),
    )
    return program

def create_shader_program_w_geometry(vertex_source: str, fragment_source: str, geometry_source: str):
    program = compileProgram(
        compileShader(vertex_source, GL_VERTEX_SHADER),
        compileShader(fragment_source, GL_FRAGMENT_SHADER),
        compileShader(geometry_source, GL_GEOMETRY_SHADER),
    )
    return program
