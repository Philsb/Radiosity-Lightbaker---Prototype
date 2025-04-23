# Radiosity Lightmap Baker (Python Prototype)

This project is a prototype implementation of a **radiosity light baking system**, based on concepts from [Hugo Elias's Radiosity Page](http://www.hugi.scene.org/online/coding/hugo_radiosity.htm)
**Note:** This project is not optimized for performance and will most likely be **ported to C++** in the future to improve speed and scalability.

## Implementation Overview

### High-Level Steps:

1. **Scene Loading**  
   `radiosityBaker.py` loads the `scene.json` and associated mesh resources. Each object must contain:
   - A **UV map** used for lightmap baking.
   - A **vertex color layer** representing diffuse color (albedo).

2. **Custom Rasterization Pass**  
   A **rasterization pass** is executed to bake essential per-texel data into the UV layout:
   - **Position Map** — stores the world position of each texel.
   - **Normal Map** — stores surface normals for shading calculations.
   - **Mask/Id Map** — stores a binary mask indicating valid texel coverage.

3. **Patch Normalization Factor**  
   Following Hugo Elias’s technique, a **normalization factor/divisor** is computed for each lightmap resolution. Each resolution has a different factor. 

6. **Radiosity Iterations**  
   - For each **valid texel** in the lightmap:
     - The scene is **rendered from the texel's position**.
     - The final radiosity value for that texel is computed by **summing the cubemap pixels mutiplied by the mutiplier image** and then **dividing by a normalization factor**. (This is explain by Hugo in his article)
   
   > ⚠️ **Note:**  
   > The multiplier image is based on the **distortion compensation formula used by Hugo Elias** in his radiosity baker.  
   > In this implementation, an **additional attenuation** is applied by multiplying each direction’s weight by the **inverse square of the distance** from the texel (camera) to the point where that direction intersects a unit cube. 
   >This is kinda confusing, and explained better in the article, but this is useful so the direct lights don't look like they that have a square-ish falloff.
   >  
   > Final formula:  
   > `multiplier = hugo_elias_multiplier * (1 / d²)`  
   > Where d is the distance the texel (camera) to the point where that direction intersects a unit cube.

7. **Output**  
   For each iteration the lightmaps values are computed and saved to disk.

---

> ⚠️ **Important Notes:**  
> - This implementation is a **prototype**, and performance is not yet optimized.  
> - A **future C++ port** is planned for better performance and scalability.  
> - Only **one UV map** and **one vertex color layer** per mesh are supported at this stage.  
> - Scenes must be **exported with the provided Blender scripts** for compatibility.

## 📦 Prerequisites

Install all required libraries using pip:

```bash
pip install -r requirements.txt
```
## 🚀 Usage

### 1. Export a Scene
You can either:
- Use one of the **example scenes** included in the repository (see `Examples/` folder).
- **Export a custom scene** from Blender using the provided export scripts (see `BlenderScripts/` folder).

### 2. Configure Lightmaps
Edit the exported `scene.json` to:
- Set the **lightmap resolution** for each object.
- Set the **intensity** for each light.

### 3. Run the Radiosity Baker
Execute the `radiosityBaker.py` script with the following arguments:

### Required Arguments
| Argument | Description |
|--------|------------------|
|-s, --scenePath | Path to the exported scene JSON (e.g., scene.json)|
|-r, --resourcesPath | Path to the mesh resources folder|
|-o, --outputPath | Directory where baked lightmaps .EXR will be saved. If it doesn't exist, it will be created automatically.|

### Optional Arguments
|Argument | Description|
|--------|------------------|
|-q, --cubemapQuality | Resolution of each cubemap face (default: 128)|
|-i, --iterations | Number of bounce iterations (default: 5)|

### Example Usage

```bash
python python radiosityBaker.py -s ./Examples/Scene1/scene1.json -r ./Examples/Scene1/Resources/ -o ./scene1Output/ -q 64 -i 8
```

## Custom Blender Scripts

This project uses a custom mesh format and in order to export your custom scene and/or meshes for the Radiosity Baker, you'll need to run  custom Blender scripts: `ExportMesh.py` and `ExportScene.py`. These scripts help export the necessary data from Blender into a format that the Radiosity Baker can process.

#### 1. **ExportMesh.py**

Use `ExportMesh.py` script to export meshes from a blender file.

**Instructions:**

1. Select all the meshes and lights meshes that you want to export. 
2. Paste the `ExportMesh.py` script into Blender's script editor.
3. Add in script **export directory** where the mesh data should be saved.
4. Run the script to export the selected meshes.

**⚠️ Very Important:** Each mesh (even the light/emissive meshes ones) should contain a UV channel for the lightmaps UV and vertex colors for the colors of the light and the meshes. The script will not run if the meshes don't contain those attributes.

#### 2. **ExportScene.py**

The `ExportScene.py` script exports the scene objects, including information about the lights in the scene, into a `.json` file. This file is essential for the Radiosity Baker to know the configuration of your scene.

**Instructions:**

1. Organize your scene lights into a separate collection called **"Lights"**. This collection should contain only the light objects/meshes that you want to export.
2. Paste the `ExportScene.py` script into Blender's script editor.
3. Add in script **export directory** where the mesh data should be saved. Along with **scene name** (e.g., scene.json).
4. Run the script to export the scene data.
5. After the **scene.json** is created you can modify the resolution and name of the lightmap for each object. Aswell as the intensity of each light.

**⚠️ Notes:**

- The **"Lights"** are meshes with an emissive property, not blender's light objects.
- The **"Lights"** colors are given by the vertex colors.

## 🔧 Improvements & Limitations

- ⚠️ **Performance:**  
  This implementation is suitable only for **small scenes with simple geometry**. It becomes **extremely slow at resolutions above 512** for each lightmap. Much performance improvements are needed.

- ⚠️ **Simplified lighting model:**  
  - **Lights are treated as emissive meshes only.**  
    - 💡 This means **no support for directional lights, point lights, spotlights, or environment maps**.  
    - All lighting must be represented by geometry with vertex color, the vertex color gives the light the color.
    - 🔦 **If you need a different kinds of lights, you will have to simulate them** by approximating them with meshes.

- ⚠️ **Lack of advanced features:**  
  - **No textures, nor materials on each mesh, no PBR support for the lighting model. Just fully rough albedo.** 
  - **Does not bake spherical harmonics or directional irradiance maps** (Future Improvement?)

- ⚠️ **UV and vertex color dependency:**  
  - A dedicated **UV channel for the lightmap** must be precomputed (e.g., unwrapped manually in Blender).  
  - **Vertex colors are required** for all meshes/light meshes — even if the mesh is meant to be plain white, a white vertex color must be assigned.  
    - 💡 This could be improved by automatically assigning a default white vertex color in the mesh exporter script.
  - Light meshes also need a UV and Vertex Color attribute, even if they don't use the UV.

- **Direct Light Artifacts**: In some cases, direct light bounces can result in artifacts. These can be mitigated by increasing the resolution of the cubemap used for rendering. But will not delete them.

- **Black edges**: Since background of the lightmaps is black, there is a risk of this "blackness" bleeding into the lightmap. This effect happens at the seams between UV islands, causing a dark edge or patch.
  - **Fix**: This can be mitigated using image editing tools like Photoshop by **dilating the colors UV islands on the borders**. A mask map is provided for each lightmap specifically for this purpose, making it easy to dilate the lightmap and reduce bleeding.

🛠️ **Note:**  
This is an experimental and educational implementation. I want to **port it to C++** in the future and turn it into a **formal, optimized tool** capable of handling larger scenes and supporting more advanced lighting features.

## Showcase
The radiosity solution converges over multiple iterations. Below is a visualization of the lightmap improving with each pass:

### Scene 1

| Pass # | Scene Preview |
|--------|------------------|
| 1      | <img src="/Examples/Scene1/scene1_pass1.png" width="200"/>|
| 2      | <img src="/Examples/Scene1/scene1_pass2.png" width="200"/>|
| 3      | <img src="/Examples/Scene1/scene1_pass3.png" width="200"/>|
| 4      | <img src="/Examples/Scene1/scene1_pass4.png" width="200"/>|
| 5      | <img src="/Examples/Scene1/scene1_pass5.png" width="200"/>|

### Scene 2

| Pass # | Scene Preview |
|--------|------------------|
| 1      | <img src="/Examples/Scene2/scene2_pass1.png" width="200"/>|
| 2      | <img src="/Examples/Scene2/scene2_pass2.png" width="200"/>|
| 3      | <img src="/Examples/Scene2/scene2_pass3.png" width="200"/>|
| 4      | <img src="/Examples/Scene2/scene2_pass4.png" width="200"/>|
| 5      | <img src="/Examples/Scene2/scene2_pass5.png" width="200"/>|

### Scene 3

| Pass # | Scene Preview |
|--------|------------------|
| 1      | <img src="/Examples/Scene3/scene3_pass1.png" width="200"/>|
| 2      | <img src="/Examples/Scene3/scene3_pass2.png" width="200"/>|
| 3      | <img src="/Examples/Scene3/scene3_pass3.png" width="200"/>|
| 4      | <img src="/Examples/Scene3/scene3_pass4.png" width="200"/>|
| 5      | <img src="/Examples/Scene3/scene3_pass5.png" width="200"/>|


## 🎓 Credits

I used these articles as my main references:

- [Radiosity, by Hugo Elias](https://www.jmeiners.com/Hugo-Elias-Radiosity/)  
  Main reference for the algorithm.

- [My first lightmap baker: Bakery, by limztudio](https://limztudio.github.io/post/bakery_mark_1/)  
  Great overview of a bunch of implementations, including Hugo's.

- [Hemicube Rendering and Integration, by  Ignacio Castaño](http://the-witness.net/news/2010/09/hemicube-rendering-and-integration/#Integration)  
  Interesting improvements to the method, eliminating artifacts.

