# django-cad-inspector
Import CAD drawings into [Django](https://djangoproject.com) and inspect them in VR with [A-Frame](https://aframe.io/docs/1.6.0/introduction/)
## Requirements
This project is tested on Django 5.1.2 and Python 3.12. It's moving from a Django project to a Python package, so some of the info below is outdated.
## Installation
Clone this repository (`git clone https://github.com/andywar65/django-cad-inspector`) and be sure to install required packages (`python -m pip install -r requirements.txt`). Add `cadinspector` to `INSTALLED_APPS` and `path("3d/", include("cadinspector.urls", namespace="cadinspector"))` to your project `urls.py`, then migrate. Reference to the included `base.html` template to see which libraries are required to be uploaded.
## Usage
Navigate to `http://127.0.0.1:8000/3d/` and you will be presented with a `Scene list`. Of course there still are no scenes, so navigate to the `Entity list`: we first have to create some entities, and then stage them on the scene.
### Entities
Click on the `Add entity` button, enter a `Title` and create the entity, then enter an `*.obj file`. If provided, enter the `*.mtl file` and eventual images. If no material is provided, you can add a color. Check the `Switch` field if your object was created in CAD: A-Frame coordinate system is rotated with respect to CAD coordinate system. As you update the entity, you will be redirected to an A-Frame window to check if everything is ok.
Alternatively you can upload a `*.gltf file`, which is the recommended format in A-Frame. If uploaded, all other formats will be neglected.
### Scenes
Now that you have some entities, go back to the `Scene list` and create a scene. Enter a `Title` and eventually an `Equirectangular image` to simulate the environment (skip the `DXF` field), create the scene then `Add staged entities`. Select one of the `Entities` you created previously, adjust `color`, `position`, `rotation` and `scale`. Stage as many entities you want (even multiple specimens of the same entity), then update the Scene. You will be redirected to an A-Frame window to check if everything is ok.
### Scenes from a DXF
It's possible to create `*.obj files` directly from `CAD`. Generate a `DXF` file with some `meshes` (if you have `3DSolids` you have to convert them to `Meshes`). Navigate to `http://127.0.0.1:8000/3d/` and click on the `Add scene` button. Enter title, description and upload a DXF file. Thanks to the outstanding library [ezdxf](https://ezdxf.mozman.at/) meshes are converted to `*.obj files`. `CAD Layer` colors will be associated to stagings. Switch to the A-Frame window, and move the cursor on imported entities: a popup will notify its Layer name.
WARNING: updating the `DXF file` will remove all entities staged on the Scene, but not the entities. If you want to remove orphan entities navigate to `http://127.0.0.1:8000/3D/entities/unstaged/` and click the `Delete All` button.
Also `Blocks` with `meshes` will be imported, each `Block` will be transformed into an `Entity`, while `Insertions` will be transformed into `Stagings`. Switch to the A-Frame window, and move the cursor on imported blocks: a popup will notify its Block name, Layer name and a list of block attributes (if any).
WARNING, some restrictions occour for insertions when pitch rotation is 90 or -90 degrees.
### A-Frame Visual Inspector
Once in the A-Frame window, if you press `Ctrl + Alt + i` you will open the [A-Frame Visual Inspector](https://aframe.io/docs/1.6.0/introduction/visual-inspector-and-dev-tools.html). It's possible to modify objects in the Inspector, save a `*.gltf file` from the whole scene, and then add it to an `Entity`.
## Next steps
Create entities with basic geometries, add lights to scenes.
## Tests
Testing is done with unittest. Coverage is 97%
