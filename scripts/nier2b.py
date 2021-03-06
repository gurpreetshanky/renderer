"""Preprocess the NieR Automata 2B model

The model is available for download from
    https://sketchfab.com/models/cec89dce88cf4b3082c73c07ab5613e7

The Python Imaging Library is required
    pip install pillow
"""

from __future__ import print_function

import json
import os
import zipfile

from PIL import Image

from utils.gltf import dump_obj_data, load_node_data

SRC_FILENAME = "nierautomata__2b.zip"
DST_DIRECTORY = "../assets/nier2b"

IMG_FILENAMES = {
    "textures/B_Swords_withoutanimation02_-_Default_baseColor.png": "sword_diffuse.tga",
    "textures/Material_25_baseColor.png": "suit_diffuse.tga",
    "textures/Material_26_baseColor.png": "head_diffuse.tga",
    "textures/Material_27_0_baseColor.png": "hair0_diffuse.tga",
    "textures/Material_27_1_baseColor.png": "hair1_diffuse.tga",
    "textures/Material_28_baseColor.png": "hair2_diffuse.tga",
}


def process_meshes(zip_file):
    gltf = json.loads(zip_file.read("scene.gltf"))
    buffer = zip_file.read("scene.bin")

    for mesh_index in range(len(gltf["meshes"])):
        obj_data = dump_obj_data(gltf, buffer, mesh_index)
        obj_filename = "nier2b{}.obj".format(mesh_index)
        obj_filepath = os.path.join(DST_DIRECTORY, obj_filename)
        with open(obj_filepath, "w") as f:
            f.write(obj_data)


def load_image(zip_file, filename):
    with zip_file.open(filename) as f:
        image = Image.open(f)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        return image


def save_image(image, filename):
    image = image.resize((512, 512), Image.LANCZOS)
    filepath = os.path.join(DST_DIRECTORY, filename)
    image.save(filepath, rle=True)


def process_images(zip_file):
    for old_filename, tga_filename in IMG_FILENAMES.items():
        image = load_image(zip_file, old_filename)
        save_image(image, tga_filename)


def print_transforms(zip_file):
    gltf = json.loads(zip_file.read("scene.gltf"))
    nodes = load_node_data(gltf)

    transforms = []
    for node in nodes:
        if node.mesh is not None:
            transforms.append(node.world_transform)

    row_pattern = "            {{{:11.6f}f, {:11.6f}f, {:11.6f}f, {:11.6f}f}},"
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
