.. _nbsphinx-link: https://github.com/vidartf/nbsphinx-link

nbsphinx-multilink
==================

A fork of nbsphinx-link_ -- a sphinx extension for including notebook
files from outside the sphinx source root. This fork simply brings the ability to add
*multiple* notebooks in a single .nblink file.

Normally, Sphinx will only allow you to add files that are situated
inside the source directory, but you might want to include files from
another directory, for example a central 'examples' folder. For RST
files these can be linked with `include` directives inside another
RST file. For notebooks, there's nbsphinx-multilink!

Usage
-----

- Install the package. ``python -m pip install -U nbsphinx-multilink``
- Add ``nbsphinx_multilink`` to extensions in Sphinx config ``conf.py``
- Add a file with the ``.nblink`` extension where you want them included.

The ``.nblink`` file is a JSON file with the following structure::

    {
        "path": "relative/path/to/notebook"
    }

Optionally the "extra-media" key can be added, if your notebook includes
any media, i.e. images. The value needs to be an array of strings,
which are paths to the media files or directories to include. Note that
this is not needed if the images are added as attachments to markdown
cells.

To include *multiple* multiple notebooks in a single .nblink file, use the following structure::

    [
        {
            "path": "relative/path/to/notebook"
        },
        {
            "path": "relative/path/to/notebook_2"
        }
    ]
