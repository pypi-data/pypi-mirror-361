# Welcome to the Imaging Server Kit's documentation!

The **Imaging Server Kit** is an open-source Python package for deploying image analysis algorithms as web services.

- Run computations remotely, while client applications remain focused on visualization.
- Connect to an algorithm server and run algorithms from [QuPath](https://github.com/Imaging-Server-Kit/qupath-extension-serverkit), [Napari](https://github.com/Imaging-Server-Kit/napari-serverkit), and Python.

## Key Features

- Turn standard Python functions into fully-featured image processing web servers with minimal effort.

```python
@algorithm_server({"image": ImageUI()})
def segmentation_server(image):
    segmentation = # your code here
    return [(segmentation, {}, "mask")]
```

## Supported image analysis tasks

| Task              | Examples                        | Napari | QuPath |
|-------------------|---------------------------------| ------ | ------ |
| Segmentation     | [StarDist](https://github.com/Imaging-Server-Kit/imaging-server-kit/tree/main/examples/servers/serverkit-stardist), [CellPose](https://github.com/Imaging-Server-Kit/imaging-server-kit/tree/main/examples/servers/serverkit-cellpose), [Rembg](https://github.com/Imaging-Server-Kit/imaging-server-kit/tree/main/examples/servers/serverkit-rembg), [SAM-2](https://github.com/Imaging-Server-Kit/extra-examples/tree/main/examples/serverkit-sam2), [InstanSeg](https://github.com/Imaging-Server-Kit/extra-examples/tree/main/examples/serverkit-instanseg)               | ✅ | ✅ |
| Object detection | [YOLO](https://github.com/Imaging-Server-Kit/imaging-server-kit/tree/main/examples/servers/serverkit-yolo), [Spotiflow](https://github.com/Imaging-Server-Kit/extra-examples/tree/main/examples/serverkit-spotiflow), [LoG detector](https://github.com/Imaging-Server-Kit/imaging-server-kit/tree/main/examples/servers/serverkit-skimage-log)    | ✅ | ✅ |
| Vector fields    | [Orientationpy](https://github.com/Imaging-Server-Kit/imaging-server-kit/tree/main/examples/servers/serverkit-orientationpy)                   | ✅ | ✅ |
| Object tracking  | [Trackpy](https://github.com/Imaging-Server-Kit/imaging-server-kit/tree/main/examples/servers/serverkit-trackpy), [Trackastra]()         | ✅ |  |
| Image-to-Image   | [SPAM](https://github.com/Imaging-Server-Kit/extra-examples/tree/main/examples/serverkit-spam), [Noise2Void](https://github.com/Imaging-Server-Kit/extra-examples/tree/main/examples/serverkit-n2v), [StackReg](https://github.com/Imaging-Server-Kit/imaging-server-kit/tree/main/examples/servers/serverkit-stackreg)         | ✅ |  |
| Text-to-Image    | [Stable Diffusion](https://github.com/Imaging-Server-Kit/extra-examples/tree/main/examples/serverkit-stable-diffusion)         | ✅ |  |
| Image-to-Text    | [Image captioning](https://github.com/Imaging-Server-Kit/extra-examples/tree/main/examples/serverkit-blip-captioning)         | ✅ |  |
| Classification   | [ResNet50](https://github.com/Imaging-Server-Kit/extra-examples/tree/main/examples/serverkit-resnet50)         | ✅ |  |

## Installation

Install the `imaging-server-kit` package with `pip`:

```
pip install imaging-server-kit
```

or clone the project and install the development version:

```
git clone https://github.com/Imaging-Server-Kit/imaging-server-kit.git
cd imaging-server-kit
pip install -e .
```

## License

This software is distributed under the terms of the [BSD-3](http://opensource.org/licenses/BSD-3-Clause) license.

## Citing

If you use `imaging-server-kit` in the context of scientific publication, you can cite it as below.

BibTeX:

```
@software{mallory_wittwer_2025_15673152,
  author       = {Mallory Wittwer and Edward Andò and Maud Barthélemy and Florian Aymanns},
  title        = {Imaging-Server-Kit/imaging-server-kit: v0.0.14},
  url          = {https://doi.org/10.5281/zenodo.15673152},
  doi          = {10.5281/zenodo.15673152},
  version      = {v0.0.14},
  year         = 2025,
}
```