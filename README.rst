
nbsphinx-link
=============

A sphinx extension for including notebook files from outside the
sphinx source root.

Normally, Sphinx will only allow you to add files that are situated
inside the source directory, but you might want to include files from
another directory, for example a central 'examples' folder. For RST
files these can be linked with `include` directives inside another
RST file. For notebooks, there's nbsphinx-link!

Usage
-----

- Install the package.
- Add 'nbsphinx_link' to extensions in Sphinx config 'conf.py'
- Add a file with the '.nblink' extension where you want them included.

The .nblink file is a JSON file with the following structure::

    {
        "path": "relative/path/to/notebook"
    }

Optionally the "extra-media" key can be added, if your notebook includes
any media, i.e. images. The value needs to be an array of strings,
which are paths to the media files or directories to include. Note that
this is not needed if the images are added as attachments to markdown
cells.

Further keys might be added in the future.

Note that the documentation of this project might serve as a
further resource!
