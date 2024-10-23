# django-cad-inspector
Import CAD drawings into [Django](https://djangoproject.com) and inspect them in VR with [A-Frame](https://aframe.io/docs/1.6.0/introduction/)
## Requirements
This project is tested on Django 5.1.2 and Python 3.12. It heavily relies on outstanding [ezdxf](https://ezdxf.mozman.at/) for handling DXF files, [django-colorfield](https://github.com/fabiocaccamo/django-colorfield) for admin color fields.
## Installation from PyPI
Activate your virtual environment and install with:
```
python -m pip install django-cad-inspector
```
In your Django project add:
```python
INSTALLED_APPS = [
    # ...
    "colorfield",
    "cadinspector",
]
```
```python
# my_project/urls.py
urlpatterns = [
    # ...
    path('3d/', include('cadinspector.urls', namespace = 'cadinspector')),
]
```
Add two lists to `my_project/settings.py`:
```python
CAD_LAYER_BLACKLIST = [...]
CAD_BLOCK_BLACKLIST = [...]
```
Here you can store names of layers and blocks you don't want to be processed.
Migrate and create a superuser.
### Templates
You also need a `base.html` template with following template blocks (a sample `base.html` is provided among package templates).
```
{% block extra-head %}
{% end block extra-head %}
...
{% block content %}
{% endblock content %}
```
Package comes with four templates, `cadinspector/entity_list.html`, `cadinspector/entity_detail.html`, `cadinspector/scene_list.html` and `cadinspector/scene_detail.html`. Copy and override them in your project templates if you want to add your styles.
## Usage
Run the server and navigate to `http://127.0.0.1:8000/3d`: you will be presented with a `Scene list`. Of course there still are no scenes, so clik on the details and on the `Add Scene` link. Enter your credentials to access the `admin site`.
### Scenes from a DXF
Enter title, description and eventually an `Equirectangular image` to simulate the environment, then upload a `DXF` file (it is a `CAD` exchange file). The `DXF` file must contain some `meshes` (if you have `3DSolids` you have to convert them to `Meshes`). Click on the `Save and continue` button.  Thanks to the outstanding [ezdxf](https://ezdxf.mozman.at/) library, meshes are converted to `*.obj files`, incorporated into `Entity` models and associated to the `Scene` via `Staging` inlines. Each Staging holds information for position, rotation, scale, color (extracted from the `CAD Layer` the mesh belonged to) and some data (more on that later). WARNING: updating the `DXF file` will remove all entities staged on the Scene, but not the entities.
Also `CAD Blocks` with `meshes` will be imported, each `Block` will be transformed into an `Entity`, while `Insertions` will be transformed into `Stagings` and associated to the `Scene`. In the case of `Blocks`, the appended data will contain also `Block attributes`. WARNING, some restrictions occour for insertions when pitch rotation is 90 or -90 degrees.
Visit the site at `http://127.0.0.1:8000/3d` again. Finally the `Scene` is listed. Click on the link and access the `A-Frame` virtual reality: hold down the right mouse button to look around, and use `WASD` keys to move. When the cursor moves on an object, a popup with data should appear (if data is associated to the staged entity).
### Entities
You can create `Entities` navigating to `http://127.0.0.1:8000/admin/cadinspector/entity/add/`: enter a Title and Description, then upload an `*.obj file`. If provided, the associated `*.mtl file` and eventual images. Check the `Switch` field if your object was created in CAD: A-Frame coordinate system is rotated with respect to CAD coordinate system.
Alternatively you can upload a `*.gltf file`, which is the recommended format in A-Frame. If uploaded, all other formats will be ignored.
### Add Entities to Scenes
In `http://127.0.0.1:8000/admin/cadinspector/scene/` choose a Scene to update. Add a `Staged entitiy`, select one of the `Entities` you created previously, adjust `color`, `position`, `rotation` and `scale`. Stage as many entities you want (even multiple specimens of the same entity), then update the Scene.
### A-Frame Visual Inspector
Once in the A-Frame window, if you press `Ctrl + Alt + i` you will open the [A-Frame Visual Inspector](https://aframe.io/docs/1.6.0/introduction/visual-inspector-and-dev-tools.html). It's possible to modify objects in the Inspector, save a `*.gltf file` from the whole scene, and then add it to an `Entity`.
## Next steps
Create entities with lights to scenes, add shadows and some physics.
## Tests
Testing is done with unittest. At the moment coverage is 97%. Tested for Django 4.2 against Python 3.9, 3.10, 3.11, 3.12 versions and for Django 5.1 against Python 3.10, 3.11, 3.12 versions (3.13 on Windows).
