# Radiosity Lightmap Baker (Prototype)

This is a **prototype** radiosity lightmap baker implemented in Python. It is designed for educational and experimentation purposes.
**Note:** This project is not optimized for performance and will most likely be **ported to C++** in the future to improve speed and scalability.

---

## Features

- Radiosity lightmap baking based of Hugo Elias' article.
- Supports:
  - A single **UV map** per object (used for lightmap baking).
  - One **vertex color layer** exported from Blender.
  - Exporting to .EXR
- Simple Python implementation for easy debugging and testing.

## Instalation

## Implementation Overview

## Examples

The radiosity solution converges over multiple iterations. Below is a visualization of the lightmap improving with each pass:

### Scene 1

| Pass # | Lightmap Preview |
|--------|------------------|
| 1      | <img src="/Examples/Scene1/scene1_pass1.png" width="200"/> |
| 2      | ![Pass 2](/Examples/Scene1/scene1_pass2.png) |
| 3      | ![Pass 3](/Examples/Scene1/scene1_pass3.png) |
| 4      | ![Pass 4](/Examples/Scene1/scene1_pass4.png) |
| 5      | ![Pass 5](/Examples/Scene1/scene1_pass5.png) |