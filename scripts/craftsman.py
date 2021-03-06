"""Preprocess the Noble Craftsman model

The model is available for download from
    https://sketchfab.com/models/0e8ff87ffaa24731b2474badebca870d

The Python Imaging Library is required
    pip install pillow
"""

from __future__ import print_function

import json
import os
import zipfile

from PIL import Image

from utils.gltf import dump_obj_data, load_node_data

SRC_FILENAME = "the_noble_craftsman.zip"
DST_DIRECTORY = "../assets/craftsman"

OBJ_FILENAMES = [
    "anvil.obj",
    "smith.obj",
    "floor.obj",
    "shoulderpad0.obj",
    "hammer.obj",
    "hotiron.obj",
    "shoulderpad1.obj",
    "spark.obj"
]

IMG_FILENAMES = {
    "textures/02_-_Default_baseColor.png": "smith_diffuse.tga",
    "textures/02_-_Default_emissive.jpg": "smith_emission.tga",
    "textures/03_-_Default_baseColor.png": "floor_diffuse.tga",
    "textures/08_-_Default_baseColor.png": "spark_diffuse.tga",
    "textures/08_-_Default_emissive.jpg": "spark_emission.tga",
    "textures/09_-_Default_baseColor.jpg": "anvil_diffuse.tga",
}


def process_meshes(zip_file):
    gltf = json.loads(zip_file.read("scene.gltf"))
    buffer = zip_file.read("scene.bin")

    for mesh_index, filename in enumerate(OBJ_FILENAMES):
        obj_data = dump_obj_data(gltf, buffer, mesh_index)
        filepath = os.path.join(DST_DIRECTORY, filename)
        with open(filepath, "w") as f:
            f.write(obj_data)


def load_image(zip_file, filename):
    with zip_file.open(filename) as f:
        image = Image.open(f)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        return image


def save_image(image, filename, size=(512, 512)):
    image = image.resize(size, Image.LANCZOS)
    filepath = os.path.join(DST_DIRECTORY, filename)
    image.save(filepath, rle=True)


def process_images(zip_file):
    for old_filename, tga_filename in IMG_FILENAMES.items():
        image = load_image(zip_file, old_filename)
        if "spark_" in tga_filename:
            save_image(image, tga_filename, size=(128, 128))
        else:
            save_image(image, tga_filename)


def print_transforms(zip_file):
    gltf = json.loads(zip_file.read("scene.gltf"))
    nodes = load_node_data(gltf)
    nodes = [node for node in nodes if node.mesh is not None]

    transforms = []
    for node in nodes:
        if node.world_transform not in transforms:
            transforms.append(node.world_transform)

    row_pattern = "            {{{:10.6f}f, {:10.6f}f, {:10.6f}f, {:10.6f}f}},"
    print("    mat4_t transforms[{}] = {{".format(len(transforms)))
    for transform in transforms:
        print("        {{")
        for i in range(4):
            print(row_pattern.format(*transform.data[i]))
        print("        }},")
    print("    };")


def main():
    if not os.path.exists(DST_DIRECTORY):
        os.makedirs(DST_DIRECTORY)

    with zipfile.ZipFile(SRC_FILENAME) as zip_file:
        process_meshes(zip_file)
        process_images(zip_file)
        # print_transforms(zip_file)


if __name__ == "__main__":
    main()
