# django-cad-inspector
Import CAD drawings into [Django](https://djangoproject.com) and inspect them in VR with [A-Frame](https://aframe.io/docs/1.6.0/introduction/)
## Requirements
This project is tested on Django 5.2 and Python 3.13 and Django 6.0 and Python 3.14. It heavily relies on outstanding [ezdxf](https://ezdxf.mozman.at/) for handling DXF files, [django-colorfield](https://github.com/fabiocaccamo/django-colorfield) for admin color fields.
## Installation from PyPI
WARNING: see below before upgrading to version 0.4.0, breaking changes!
Activate your virtual environment and install with:
```
python -m pip install django-cad-inspector
```
In your Django project add:
```python
INSTALLED_APPS = [
    # ...
    "colorfield",
    "django_cad_inspector",
]
```
```python
# my_project/urls.py
urlpatterns = [
    # ...
    path('3d/', include('django_cad_inspector.urls', namespace = 'django_cad_inspector')),
]
```
Add two lists to `my_project/settings.py`:
```python
CAD_LAYER_BLACKLIST = [...]
CAD_BLOCK_BLACKLIST = [...]
```
Here you can store names of layers and blocks you don't want to be processed.
Migrate and create a superuser.
### Upgrading to version >=0.4.0 from earlier
Some breaking changes (app name change). Before upgrading download your models as fixtures: `python manage.py dumpdata cadinspector -o somefile.json`, open the file and change all occourences of `cadinspector.` into `django_cad_inspector.`. Finally upgrade the package and reload the fixtures: `python manage.py loaddata somefile.json`
### Templates
You also need a `base.html` template with following template blocks (a sample `base.html` is provided among package templates).
```
{% block extra-head %}
{% end block extra-head %}
...
{% block content %}
{% endblock content %}
```
Package comes with four templates, `django_cad_inspector/entity_list.html`, `django_cad_inspector/entity_detail.html`, `django_cad_inspector/scene_list.html` and `django_cad_inspector/scene_detail.html`. Copy and override them in your project templates if you want to add your styles.
## Usage
Run the server and navigate to `http://127.0.0.1:8000/3d`: you will be presented with a `Scene list`. Of course there still are no scenes, so clik on the details and on the `Add Scene` link. Enter your credentials to access the `admin site`.
### Scenes from a DXF
Enter title, description and eventually an `Equirectangular image` to simulate the environment, then upload a `DXF` file (it is a `CAD` exchange file). The `DXF` file must contain some `meshes` (if you have `3DSolids` you have to convert them to `Meshes`). Click on the `Save and continue` button.  Thanks to the outstanding [ezdxf](https://ezdxf.mozman.at/) library, meshes are converted to `*.obj files`, incorporated into `Entity` models and associated to the `Scene` via `Staging` inlines. Each Staging holds information for position, rotation, scale, color (extracted from the `CAD Layer` the mesh belonged to) and some data (more on that later). WARNING: updating the `DXF file` will remove all entities staged on the Scene, but not the entities.
Also `CAD Blocks` with `meshes` will be imported, each `Block` will be transformed into an `Entity`, while `Insertions` will be transformed into `Stagings` and associated to the `Scene`. In the case of `Blocks`, the appended data will contain also `Block attributes`. WARNING, some restrictions occour for insertions when pitch rotation is 90 or -90 degrees.
Visit the site at `http://127.0.0.1:8000/3d` again. Finally the `Scene` is listed. Click on the link and access the `A-Frame` virtual reality: hold down the right mouse button to look around, and use `WASD` keys to move. When the cursor moves on an object and you click on it, a popup with data should appear (if data is associated to the staged entity). Leave the object and the popup will disappear.
### Entities
You can create `Entities` navigating to `http://127.0.0.1:8000/admin/django_cad_inspector/entity/add/`: enter a Title and Description, then upload an `*.obj file`. If provided, the associated `*.mtl file` and eventual images. Check the `Switch` field if your object was created in CAD: A-Frame coordinate system is rotated with respect to CAD coordinate system.
Alternatively you can upload a `*.gltf file`, which is the recommended format in A-Frame. If uploaded, all other formats will be ignored.
### Add Entities to Scenes
In `http://127.0.0.1:8000/admin/django_cad_inspector/scene/` choose a Scene to update. Add a `Staged entity`, select one of the `Entities` you created previously, adjust `color`, `position`, `rotation` and `scale`. Stage as many entities you want (even multiple specimens of the same entity), then update the Scene.
### Shadows
When inspecting a scene, click on the dropdown next to the scene title: you will be able to inspect the scene without popups and / or with shadows casted on entities. The latter functionality is resource consuming.
## Entity utilities
Navigating to `http://127.0.0.1:8000/admin/django_cad_inspector/entity/` shows list of existing `Entities`. Two admin actions are implemented to manage them:
### Check file names
Uploading `*.mtl file` and images in Django may change their filename, i.e. to avoid duplicate filenames. This can lead `*.obj files` and `*.mtl files` to miss their assets (filenames are hardcoded within these files). Select corrupted `Entities` and run the routine: hardcoded filenames will be rewritten to match actual uploaded filenames.
### Delete unstaged entities
As seen before, deleting a `Staging` does not delete the corresponding `Entity`, which can be staged in multiple `Scenes`. Select all `Entities` and run this routine if you want to get rid of unstaged ones.
## A-Frame Visual Inspector
Once in the A-Frame window, if you press `Ctrl + Alt + i` you will open the [A-Frame Visual Inspector](https://aframe.io/docs/1.6.0/introduction/visual-inspector-and-dev-tools.html). It's possible to modify objects in the Inspector, save a `*.gltf file` from the whole scene, and then add it to an `Entity`.
## Next steps
Create entities with lights, add some physics.
## Tests
Testing is done with unittest. At the moment coverage is 97%. Tested for Django 4.2 against Python 3.9, 3.10, 3.11, 3.12 versions, for Django 5.1 against Python 3.10, 3.11, 3.12 versions (3.13 on Windows), Django 5.2 against Python 3.13.1 and Dango 6.0 against Python 3.14.2.
## Changelog
- 0.6.0: Using Django 6.0
- 0.5.0: Using Django 5.2
- 0.4.0: Breaking change: change of app name, see install
- 0.3.2: Also Stagings in admin
- 0.3.1: Small fix to lamp position
- 0.3.0: Staged entities may be presented in wireframe mode (if upgrading from 0.2.0, migrate models). Popups show up when the entity is clicked on. You can turn on shadows casted by a portable lamp.
- 0.2.0: First working version
