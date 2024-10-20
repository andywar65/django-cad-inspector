# django-cad-inspector
Import CAD drawings into [Django](https://djangoproject.com) and inspect them in VR with [A-Frame](https://aframe.io/docs/1.6.0/introduction/)
## Requirements
This project is tested on Django 5.1.2 and Python 3.12. It heavily relies on outstanding [ezdxf](https://ezdxf.mozman.at/) for handling DXF files, [django-colorfield](https://github.com/fabiocaccamo/django-colorfield) for admin color fields. It's moving from a Django project to a Python package, so some of the info below may be outdated.
## Installation
Activate your virtual environment and install required packages with:
```
python -m pip install -r requirements.txt
```
Clone this repository:
```
git clone https://github.com/andywar65/django-cad-inspector
```
Migrate and create a superuser. Your project should be ready for use.
## Usage
Run the server and navigate to `http://127.0.0.1:8000/3d`: you will be presented with a `Scene list`. Of course there still are no scenes, so clik on the details and on the `Add Scene` link. Enter your credentials to access the `admin site`.
### Scenes from a DXF
Enter title, description and upload a `DXF` file (it is a `CAD` exchange file). The `DXF` file must contain some `meshes` (if you have `3DSolids` you have to convert them to `Meshes`). Click on the `Save and continue` button.  Thanks to the outstanding [ezdxf](https://ezdxf.mozman.at/) library, meshes are converted to `*.obj files`, incorporated into `Entity` models and associated to the `Scene` via `Staging` inlines. Each Staging holds information for position, rotation, scale, color (extracted from the `CAD Layer` the mesh belonged to) and some data (more on that later). WARNING: updating the `DXF file` will remove all entities staged on the Scene, but not the entities.
Also `CAD Blocks` with `meshes` will be imported, each `Block` will be transformed into an `Entity`, while `Insertions` will be transformed into `Stagings` and associated to the `Scene`. In the case of `Blocks`, the appended data will contain also `Block attributes`. WARNING, some restrictions occour for insertions when pitch rotation is 90 or -90 degrees.
Visit the site at `http://127.0.0.1:8000/3d` again. Finally the `Scene` is listed. Click on the link and access the `A-Frame` virtual reality: hold down the right mouse button to look around, and use `WASD` keys to move. When the cursor moves on an object, a popup with data should appear (if data is associated to the staged entity).
### Entities
Click on the `Add entity` button, enter a `Title` and create the entity, then enter an `*.obj file`. If provided, enter the `*.mtl file` and eventual images. Check the `Switch` field if your object was created in CAD: A-Frame coordinate system is rotated with respect to CAD coordinate system. As you update the entity, you will be redirected to an A-Frame window to check if everything is ok.
Alternatively you can upload a `*.gltf file`, which is the recommended format in A-Frame. If uploaded, all other formats will be neglected.
### Scenes
Now that you have some entities, go back to the `Scene list` and create a scene. Enter a `Title` and eventually an `Equirectangular image` to simulate the environment (skip the `DXF` field), create the scene then `Add staged entities`. Select one of the `Entities` you created previously, adjust `color`, `position`, `rotation` and `scale`. Stage as many entities you want (even multiple specimens of the same entity), then update the Scene. You will be redirected to an A-Frame window to check if everything is ok.
### A-Frame Visual Inspector
Once in the A-Frame window, if you press `Ctrl + Alt + i` you will open the [A-Frame Visual Inspector](https://aframe.io/docs/1.6.0/introduction/visual-inspector-and-dev-tools.html). It's possible to modify objects in the Inspector, save a `*.gltf file` from the whole scene, and then add it to an `Entity`.
## Next steps
Create entities with basic geometries, add lights to scenes.
## Tests
Testing is done with unittest. Coverage is 97%
