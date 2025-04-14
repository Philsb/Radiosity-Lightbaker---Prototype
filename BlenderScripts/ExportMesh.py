import bpy
import bmesh
import pprint
import math
import json
import base64
import struct

def get_index(list, value):
    return list.index(value)

def add_unique(list, value):
    if value not in list:
        list.append(value)
        return len(list) - 1
    else:
        return get_index(list, value)

def mesh_triangulate(me):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()

def export_obj_mesh(obj, dir_path):
    # Ensure the object is of type 'MESH'
    if obj and obj.type == 'MESH':
        
        me = obj.to_mesh(preserve_all_data_layers=True)
        mesh_triangulate(me)
        
        me.calc_normals_split()
        me.calc_smooth_groups()
        
        faces = []
        
        positions = []
        normals = []
        colors = []
        uvs = []
        lightmapUVs = []
        
        
        #Gather all triangles data
        for f in me.polygons:
            
            face_dict = {}
            face_dict["material_index"] = f.material_index
            face_dict["vertices"] = []
            
            for l_idx in f.loop_indices:
                
                #Position
                vert_index = me.loops[l_idx].vertex_index
                pos = me.vertices[vert_index].co
                pos_idx = add_unique( positions, [pos.x, pos.y, pos.z] )
                
                #Normal
                normal = me.loops[l_idx].normal
                normal_idx = add_unique( normals, [normal.x, normal.y, normal.z] )

                #Color
                color_layer = me.color_attributes["Color"].data
                vert_color = color_layer[vert_index].color
                color_idx = add_unique( colors, [vert_color[0], vert_color[1], vert_color[2]] )
                
                #TexUV
                uv_layer = me.uv_layers['UVMap'].data
                uv = uv_layer[l_idx].uv
                uv_idx = add_unique( uvs, [uv.x, uv.y] )
                
                vertex = {
                    "pos_idx": pos_idx,
                    "normal_idx": normal_idx,
                    "color_idx": color_idx,
                    "uv_idx": uv_idx,
                }
                
                face_dict["vertices"].append(vertex)
                
            faces.append(face_dict)
        
        
        #Sort faces into each segment representing each material
        segments = {}
        loop_ctr = 0
        for f in faces:
            mat_index = str(f["material_index"])
            
            if mat_index not in segments:
                segments[ mat_index ] = {
                            "vertices":[], 
                            "indices":[]
                        }
                
                
            current_segment = segments[ mat_index ]
            
            index = len( current_segment["indices"] )
            for v in f['vertices']:
                
                pos =  positions [ v["pos_idx"] ]
                norm = normals [ v["normal_idx"] ]
                vert_color = colors [ v["color_idx"] ]
                uv = uvs [ v["uv_idx"] ]
            
                #add to flattened array
                current_segment["vertices"] += [pos[0], pos[1], pos[2], 
                                            norm[0], norm[1], norm[2], 
                                            vert_color[0], vert_color[1], vert_color[2], 
                                            uv[0], uv[1]]
                
                current_segment["indices"].append(index)
               
                index += 1 
        
        final_dict = {
            "resType": "mesh",
            "meshes": [],
        
        }
        
        
        for key, segment in segments.items():
            
            # Encode the bytearray to a base64 string
            vert_array = segment["vertices"]
            vert_packed_data = struct.pack('%sf' % len(vert_array), *vert_array)
            vert_encoded_data = base64.b64encode(vert_packed_data).decode('utf-8')
            
            
            # Encode the bytearray to a base64 string
            index_array = segment["indices"]
            index_packed_data = struct.pack('%sI' % len(index_array), *index_array)
            index_encoded_data = base64.b64encode(index_packed_data).decode('utf-8')
            
                
            segment_entry = {
                "vertices": vert_encoded_data,
                "indices": index_encoded_data
            }
            
            final_dict["meshes"].append(segment_entry)

       
        file_path = dir_path + obj.name + ".mesh.json"   
        
        # the json file where the output must be stored
        out_file = open(file_path, "w")
        json.dump(final_dict, out_file, indent = 1)
        out_file.close() 
        
        print("Exported MESH to: " + file_path)    

    else:
        print("No active mesh object found.")
        
    
    
# Get the collection by name
collection = bpy.data.collections.get("Export")

for obj in bpy.context.selected_objects:
    export_obj_mesh(obj, "D:\\Users\\Felipe\\Desktop\\TestRaytracingScene\\New2\\")

        