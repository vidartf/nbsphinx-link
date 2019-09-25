"""A sphinx extension for including notebook files from outside sphinx source root.

Usage:
- Install the package.
- Add 'nbsphinx_link' to extensions in Sphinx config 'conf.py'
- Add a file with the '.nblink' extension where you want them included.

The .nblink file is a JSON file with the following structure:

{
    "path": "relative/path/to/notebook"
}

Optionally the "extra-media" key can be added, if you notebook includes
any media, i.e. images. The value can be an array or a string, with
path/-s to the media file/-s or directory/-s.

Further keys might be added in the future.
"""

import errno
import json
import os
import shutil

from docutils import io, nodes, utils
from docutils.utils.error_reporting import SafeString, ErrorString
from nbsphinx import NotebookParser, NotebookError, _ipynbversion
import nbformat
from sphinx.util.logging import getLogger

from ._version import __version__


def copy_directory(src, dest):
    """
    Copies a directory or file from the path ``src`` to ``dest``.
    Originally from: https://www.pythoncentral.io/how-to-recursively-copy-a-directory-folder-in-python/

    Parameters
    ----------
    src : str
        Path to the source directory or file
    dest : str
        Path to the destination directory or file
    """
    try:
        # ensure that files will be overwritten
        shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: {}'.format(e))


def collect_extra_media(extra_media, source_file, nb_path):
    """
    Collects extra media defined in the .nblink file, with the key 'extra-media'.
    The extra media (i.e. images) need to be copied on order nbsphinx to properly
    render the notebooks, since nbsphinx assumes that the files are relative to
    the .nblink.

    Parameters
    ----------
    extra_media : str, list
        Path/-s to directorie-/s and/or file-/s with extra media.
    source_file : str
        Path to the .nblink file.
    nb_path : str
        Path to the notebook defined in the .nblink file , with the key 'path'.
    """
    source_dir = os.path.dirname(source_file)
    if isinstance(extra_media, str):
        extra_media = [extra_media]
    for extract_media_path in extra_media:
        if os.path.isabs(extract_media_path):
            src_path = extract_media_path
        else:
            extract_media_relpath = os.path.join(source_dir, extract_media_path)
            src_path = os.path.normpath(os.path.join(source_dir, extract_media_relpath))
        target_path = utils.relative_path(nb_path, src_path)
        target_path = os.path.normpath(os.path.join(source_dir, target_path))
        if os.path.exists(src_path):
            copy_directory(src_path, target_path)
        else:
            logger = getLogger(__name__)
            logger.warning(
                'The path "{}", defined in {} "extra-media", isn\'t a valid path.'.format(
                    extract_media_path, source_file
                )
            )


class LinkedNotebookParser(NotebookParser):
    """A parser for .nblink files.

    The parser will replace the link file with the output from
    nbsphinx on the linked notebook. It will also add the linked
    file as a dependency, so that sphinx will take it into account
    when figuring out whether it should be rebuilt.

    The .nblink file is a JSON file with the following structure:

    {
        "path": "relative/path/to/notebook",
        "extra-media":
    }

    Optionally the "extra-media" key can be added, if you notebook includes
    any media, i.e. images. The value can be an array or a string, with
    path/-s to the media file/-s or directory/-s.

    Further keys might be added in the future.
    """

    supported = ('linked_jupyter_notebook',)

    def parse(self, inputstring, document):
        """Parse the nblink file.

        Adds the linked file as a dependency, read the file, and
        pass the content to the nbshpinx.NotebookParser.
        """
        link = json.loads(inputstring)
        env = document.settings.env
        source_dir = os.path.dirname(env.doc2path(env.docname))

        abs_path = os.path.normpath(os.path.join(source_dir, link['path']))
        path = utils.relative_path(None, abs_path)
        path = nodes.reprunicode(path)

        extra_media = link.get('extra-media', None)
        if extra_media:
            source_file = env.doc2path(env.docname)
            collect_extra_media(extra_media, source_file, path)

        document.settings.record_dependencies.add(path)
        env.note_dependency(path)

        target_root = env.config.nbsphinx_link_target_root
        target = utils.relative_path(target_root, abs_path)
        target = nodes.reprunicode(target).replace(os.path.sep, '/')
        env.metadata[env.docname]['nbsphinx-link-target'] = target

        # Copy parser from nbsphinx for our cutom format
        try:
            formats = env.config.nbsphinx_custom_formats
        except AttributeError:
            pass
        else:
            formats.setdefault(
                '.nblink', lambda s: nbformat.reads(s, as_version=_ipynbversion)
            )

        try:
            include_file = io.FileInput(source_path=path, encoding="utf8")
        except UnicodeEncodeError as error:
            raise NotebookError(
                'Problems with linked notebook "%s" path:\n'
                'Cannot encode input file path "%s" '
                "(wrong locale?)." % (env.docname, SafeString(path))
            )
        except IOError as error:
            raise NotebookError(
                'Problems with linked notebook "%s" path:\n%s.'
                % (env.docname, ErrorString(error))
            )

        try:
            rawtext = include_file.read()
        except UnicodeError as error:
            raise NotebookError(
                'Problem with linked notebook "%s":\n%s'
                % (env.docname, ErrorString(error))
            )
        return super(LinkedNotebookParser, self).parse(rawtext, document)


def setup(app):
    """Initialize Sphinx extension."""
    app.setup_extension('nbsphinx')
    app.add_source_suffix('.nblink', 'linked_jupyter_notebook')
    app.add_source_parser(LinkedNotebookParser)
    app.add_config_value('nbsphinx_link_target_root', None, rebuild='env')

    return {'version': __version__, 'parallel_read_safe': True}
