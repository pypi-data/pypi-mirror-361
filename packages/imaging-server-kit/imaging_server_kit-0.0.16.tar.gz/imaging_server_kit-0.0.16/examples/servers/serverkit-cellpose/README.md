![EPFL Center for Imaging logo](https://imaging.epfl.ch/resources/logo-for-gitlab.svg)
# serverkit-cellpose

Implementation of a web server for [CellPose](https://github.com/MouseLand/cellpose).

## Installing the algorithm server with `pip`

Install dependencies:

```
pip install -r requirements.txt
```

Run the server:

```
python main.py
```

The server will be running on http://localhost:8000.

## Using `docker-compose`

To build the docker image and run a container for the algorithm server in a single command, use:

```
docker compose up
```

The server will be running on http://localhost:8000.

## Sample images provenance

- `nuclei_2d.tif`: Fluorescence microscopy image and mask from the 2018 kaggle DSB challenge (Caicedo et al. "Nucleus segmentation across imaging experiments: the 2018 Data Science Bowl." Nature methods 16.12).