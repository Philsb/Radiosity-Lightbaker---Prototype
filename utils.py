import base64
import glm
import numpy as np
from PIL import Image

def base64_to_float_array(base64_string: str) -> np.ndarray:

    decoded_bytes = base64.b64decode(base64_string)
    float_array = np.frombuffer(decoded_bytes, dtype=np.float32)
    return float_array

def base64_to_uint32_array(base64_string: str) -> np.ndarray:

    decoded_bytes = base64.b64decode(base64_string)
    uint32_array = np.frombuffer(decoded_bytes, dtype=np.uint32)

    return uint32_array

def euler_to_mat4(yaw: float, pitch: float, roll: float) -> glm.quat:
    # Create quaternions from yaw, pitch, and roll
    q_yaw = glm.angleAxis(yaw, glm.vec3(0.0, 1.0, 0.0))  # Yaw around Y-axis
    q_pitch = glm.angleAxis(pitch, glm.vec3(1.0, 0.0, 0.0))  # Pitch around X-axis
    q_roll = glm.angleAxis(roll, glm.vec3(0.0, 0.0, 1.0))  # Roll around Z-axis

    # Combine the quaternions
    quaternion = q_roll * q_pitch * q_yaw  # Note the order of multiplication
    return glm.mat4_cast(glm.normalize(quaternion))

def createTransform(pos, rot, scale):
    pos_mat = glm.translate(glm.mat4(1.0), glm.vec3(pos[0], pos[1], pos[2]))  
    rot_mat = euler_to_mat4(rot[0], rot[1], rot[2])
    scale_mat = glm.scale(glm.mat4(1.0), glm.vec3(scale[0], scale[1], scale[2]))
    
    return pos_mat * rot_mat * scale_mat

def save_renderTexture_to_disk(path, width, height, image_array, format = "RGBA"):
    # Create an image from the scaled data
    image = Image.fromarray(image_array , format)
    # Flip the image vertically (OpenGL's origin is bottom-left, Pillow expects top-left)
    image = np.flip(image, axis=0)
    # Create an image from the array and save it
    img = Image.fromarray(image)
    img.save(path + ".png")
    print(path + ".png")