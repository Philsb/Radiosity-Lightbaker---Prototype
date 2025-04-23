import bpy
import json
import os

def exportSceneToJson(filepath):
    meshes = []
    lights = []

    lightsCollection = bpy.data.collections.get("Lights")

    for obj in bpy.context.scene.objects:
        objData = {
            "mesh": obj.name+".mesh.json",
            "position": [obj.location.x, obj.location.y, obj.location.z],
            "rotation": [obj.rotation_euler.x, obj.rotation_euler.y, obj.rotation_euler.z],
            "scale": [obj.scale.x, obj.scale.y, obj.scale.z]
        }

        if lightsCollection and obj.name in lightsCollection.objects:
            # For lights, add intensity
            objData["intensity"] = 1.0
            lights.append(objData)
        else:
            # For meshes, add lightmap info
            objData["lightmapTexName"] = obj.name+"_lightmap"
            objData["lightmapSize"] = 128
            meshes.append(objData)

    result = {
        "objects": meshes,
        "lights": lights
    }

    # Write to file
    with open(filepath, 'w') as f:
        json.dump(result, f, indent=4)

    print(f"Exported scene to {filepath}")
    
# Your export path here
sceneName = "scene3.json"
exportPath = ""
exportSceneToJson(exportPath + "\\" + sceneName)