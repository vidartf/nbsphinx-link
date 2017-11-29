
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
- Add 'nbsphinx-link' to extensions in Sphinx config 'conf.py'
- Add a file with the '.nblink' extension where you want them included.

The .nblink file is a JSON file with the following structure::

    {
        "path": "relative/path/to/notebook"
    }

Further keys might be added in the future.
