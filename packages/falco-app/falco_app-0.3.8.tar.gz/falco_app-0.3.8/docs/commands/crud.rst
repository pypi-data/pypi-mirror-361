:description: Faster prototyping with basic CRUD (Create, Read, Update, Delete) python views and HTML templates for your django models.

crud
====

Accelerate prototyping with basic CRUD (Create, Read, Update, Delete) python views and HTML templates, enhanced with htmx and Tailwind CSS.

.. exec_code::
    :language_output: shell

    # --- hide: start ---
    from falco.management.commands.crud import Command

    Command().print_help("manage.py", "crud")
    #hide:toggle

This command generates htmx-powered create, read, update, and delete views for your model. It follows a similar idea
as `neapolitan <https://github.com/carltongibson/neapolitan>`_, but with a completely different approach. Instead of inheriting
from a class as you would with ``neapolitan``, this command generates basic ``views``, ``urls``, ``forms``, ``admin`` (thanks to `django-extensions <https://django-extensions.readthedocs.io/en/latest/admin_generator.html>`_)
and HTML ``templates``, and updates or overrides the corresponding files in your project. I prefer this approach because, at the end, you'll have all the new code directly in front of you. It's easily
accessible and you can update it as you see fit. The idea is to accelerate project prototyping. Write a model and you instantly have views ready for it.


.. admonition:: Why function based views?
    :class: hint dropdown

    I think class-based views get complex faster than function-based views. Both have their use cases, but function-based views
    stay simpler to manage longer in my experience. There is an excellent document on the topic, read `django views the right way <https://spookylukey.github.io/django-views-the-right-way/>`_.

.. If you want to see an example of the generated code, check out the `source code of the demo project <https://github.com/Tobi-De/falco/tree/main/demo/myjourney/entries>`_.


Python code
^^^^^^^^^^^

All Python code added by this command will be in **append** mode, meaning it won't override the content of your existing files.
Instead, it will add code at the end or create the files if they are missing. The files that will be modified
are ``forms.py``, ``urls.py``, ``admin.py`` (if you have `django-extension <https://django-extensions.readthedocs.io/en/latest/index.html>`_ installed),
``views.py`` and your project root ``urls.py``.

For the sake brevity, I'll only show an example of what the ``urls.py`` file might look like for a model named ``Entry`` in a django app named ``entries``.

.. code-block:: bash

    python -m myproject entry.entries

.. literalinclude:: /_static/snippets/urls.py

As you can see, the convention is quite simple: ``<model_name_lower>_<operation>``. Note that if you don't specify the model name and run
``python -m myproject entries``, the same code with the described conventions will be generated for all the models in the ``entries`` app.

Now, if you're anything like me, the code above might have made you cringe due to the excessive repetitions of the word ``entry``.
This wouldn't have been the case if the model was called ``Category``, for example. For these specific cases, there is an ``--entry-point`` option.

Let's try it.

.. code-block:: bash

    python -m myproject entries.entry --entry-point

.. admonition:: Oops, I made a mistake
    :class: tip dropdown

    If you made a mistake when running CRUD commands and want to discard the changes and restart, you can use the following commands instead of manually deleting all changes.
    Note that the commands below will discard all current changes. You can also specify a specific path to remove only a subset of the changes.

    .. code-block:: shell

        git checkout -- . # Remove changes in the working tree
        git clean -fd # Remove untracked files and directories from the working tree

.. code-block:: python
    :caption: entries/urls.py

    from django.urls import path

    from . import views

    app_name = "entries"

    urlpatterns = [
        path("", views.index, name="index"),
        path("create/", views.create, name="create"),
        path("<int:pk>/", views.detail, name="detail"),
        path("<int:pk>/update/", views.update, name="update"),
        path("<int:pk>/delete/", views.delete, name="delete"),
    ]

Much cleaner, specifying that option means you consider the ``Entry`` model as the entry point of your ``entries`` app.
So, instead of the base URL of the app looking like ``entries/entries/``, it will just be ``entries/``.

As previously mentioned, the command will also register your app in your project root URLs configuration. This occurs when
you generate ``crud`` views for a model and there is no existing ``urls.py`` file for the app. In such cases, it is assumed
that you haven't already registered the URLs for your app since the command just created the file.

Here is an example of how the ``entries`` app will be registered.

.. code-block:: python
    :caption: config/urls.py
    :linenos:
    :emphasize-lines: 4

    urlpatterns = [
    path("admin/", admin.site.urls),
    ...
    path("entries/", include("entries.urls", namespace="entries"))
    ]



HTML templates
^^^^^^^^^^^^^^

Unlike the Python code, the generated HTML templates will overwrite any existing ones. If you want to avoid this, you should commit
your changes before running this command or use the ``--only-python`` option to generate only Python code. The files are generated
with minimal styling (using Tailwind CSS) and are reasonably presentable.
Four files are generated:

* ``<model_name_lower>_list.html``
* ``<model_name_lower>_create.html``
* ``<model_name_lower>_detail.html``
* ``<model_name_lower>_update.html``

There is no ``<model_name_lower>_delete.html`` file because deletion is handled in the ``<model_name_lower>_list.html``.
Each generated HTML file extends a ``base.html`` template. Therefore, make sure you have a top-level ``base.html`` file in
your templates directory.


.. note::

    If you use the ``--entry-point`` option, the files will be named ``index.html``, ``create.html``, ``detail.html``, and ``update.html``.

To determine where to place the generated files, we check the ``DIRS`` key in the ``TEMPLATES`` settings of your Django project.
If it is populated, we take the first value in the list and generate the template files in ``<templates_dir>/<app_label>``.
If it is not populated, we use the classic Django layout, which is ``<app_label>/templates/<app_label>``.

.. If you want an overview of what the templates look like, check out the `demo project <https://github.com/Tobi-De/falco/tree/main/demo/templates/entries>`_.

Custom Templates
****************

The ``crud`` command supports the ability to specify your own HTML templates using the ``--blueprints`` option.
This option only takes into account HTML files and will completely override the default templates. The HTML templates
use the `jinja2 <https://jinja.palletsprojects.com/en/3.1.x/>`_ syntax. To see examples of what the templates look like,
check out the base templates `here <https://github.com/Tobi-De/falco/tree/main/src/falco/crud/html>`_.

Below is an example of the context each template will receive.


.. jupyter-execute::
    :hide-code:

    from falco.management.commands.crud.model_crud import HtmlBlueprintContext
    from falco.management.commands.crud.model_crud import get_html_blueprint_context
    from falco.management.commands.crud.model_crud import DjangoModel
    from pprint import pprint

    dj_model = DjangoModel(
        name = "Entry",
        name_plural = "Entries",
        verbose_name = "Entry",
        verbose_name_plural = "Entries",
        has_file_field = False,
        has_editable_date_field = False,
        fields = {
            "name": {"verbose_name": "Name", "editable": True, "class_name": "CharField", "accessor": "{{entry.name}}"},
            "price": {"verbose_name": "Price", "editable": True, "class_name": "DecimalField", "accessor": "{{entry.price}}"},
        }
    )

    pprint(get_html_blueprint_context(app_label="entries", django_model=dj_model), sort_dicts=False, compact=True, width=120)


Examples
^^^^^^^^

Some usage examples.

.. code:: bash

    $ python -m myproject entries.entry
    $ python -m myproject entries
    $ python -m myproject entries.entry -e="secret_field1" -e="secret_field2"
    $ python -m myproject entries.entry --only-html
    $ python -m myproject entries.entry --only-python
    $ python -m myproject entries.entry --entry-point
    $ python -m myproject entries.entry --entry-point --login
    $ python -m myproject entries.entry --blueprints /path/to/blueprints
