:description: Start a new django app that's automatically registered to your installed apps.

start_app
=========

.. exec_code::
    :language_output: shell

    # --- hide: start ---
    from falco.management.commands.start_app import Command

    Command().print_help("manage.py", "start_app")
    #hide:toggle

This command executes Django's ``startapp``, along with a few additional tasks:

- It deletes the ``tests.py`` file. I never use a single test file when writing tests.
- It moves the newly created app to the ``APPS_DIR``. In the context of **Falco** projects, the ``apps_dir`` is a subdirectory in your root directory named after your project.
- It registers the new app in your settings under ``INSTALLED_APP``.
- It add a basic empty model to your ``models.py`` file.

These are tasks I always perform when generating a new app with Django. Now, I can reclaim those precious seconds I would have
spent doing this manually.

