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

| Pass # | Scene Preview |
|--------|------------------|
| 1      | <img src="/Examples/Scene1/scene1_pass1.png" width="200"/> |
| 2      | <img src="/Examples/Scene1/scene1_pass2.png" width="200"/> |
| 3      | <img src="/Examples/Scene1/scene1_pass3.png" width="200"/>|
| 4      | <img src="/Examples/Scene1/scene1_pass4.png" width="200"/>|
| 5      | <img src="/Examples/Scene1/scene1_pass5.png" width="200"/>|

### Scene 2

| Pass # | Scene Preview |
|--------|------------------|
| 1      | <img src="/Examples/Scene2/scene2_pass1.png" width="200"/> |
| 2      | <img src="/Examples/Scene2/scene2_pass2.png" width="200"/> |
| 3      | <img src="/Examples/Scene2/scene2_pass3.png" width="200"/>|
| 4      | <img src="/Examples/Scene2/scene2_pass4.png" width="200"/>|
| 5      | <img src="/Examples/Scene2/scene2_pass5.png" width="200"/>|

### Scene 3

| Pass # | Scene Preview |
|--------|------------------|
| 1      | <img src="/Examples/Scene3/scene3_pass1.png" width="200"/> |
| 2      | <img src="/Examples/Scene3/scene3_pass2.png" width="200"/> |
| 3      | <img src="/Examples/Scene3/scene3_pass3.png" width="200"/>|
| 4      | <img src="/Examples/Scene3/scene3_pass4.png" width="200"/>|
| 5      | <img src="/Examples/Scene3/scene3_pass5.png" width="200"/>|


