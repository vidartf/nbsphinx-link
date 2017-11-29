"""A sphinx extension for including notebook files from outside sphinx source root.

Usage:
- Install the package.
- Add 'nbsphinx-link' to extensions in Sphinx config 'conf.py'
- Add a file with the '.nblink' extension where you want them included.

The .nblink file is a JSON file with the following structure:

{
    "path": "relative/path/to/notebook"
}

Further keys might be added in the future.
"""


import json
import os

from docutils import io, nodes, utils
from docutils.utils.error_reporting import SafeString, ErrorString
from nbsphinx import NotebookParser, NotebookError

from ._version import __version__


class LinkedNotebookParser(NotebookParser):
    """A parser for .nblink files.

    The parser will replace the link file with the output from
    nbsphinx on the linked notebook. It will also add the linked
    file as a dependency, so that sphinx will take it into acount
    when figuring out whether it should be rebuilt.

    The .nblink file is a JSON file with the following structure:

    {
        "path": "relative/path/to/notebook"
    }

    Further keys might be added in the future.
    """
    def parse(self, inputstring, document):
        """Parse the nblink file.

        Adds the linked file as a dependency, read the file, and
        pass the content to the nbshpinx.NotebookParser.
        """
        link = json.loads(inputstring)
        env = document.settings.env
        source_dir = os.path.dirname(env.doc2path(env.docname))

        path = link['path']
        path = os.path.normpath(os.path.join(source_dir, path))
        path = utils.relative_path(None, path)
        path = nodes.reprunicode(path)

        document.settings.record_dependencies.add(path)
        env.note_dependency(path)

        try:
            include_file = io.FileInput(source_path=path, encoding='utf8')
        except UnicodeEncodeError as error:
            raise NotebookError(u'Problems with linked notebook "%s" path:\n'
                                'Cannot encode input file path "%s" '
                                '(wrong locale?).' %
                                (env.docname, SafeString(path)))
        except IOError as error:
            raise NotebookError(u'Problems with linked notebook "%s" path:\n%s.' %
                                (env.docname, ErrorString(error)))

        try:
            rawtext = include_file.read()
        except UnicodeError as error:
            raise NotebookError(u'Problem with linked notebook "%s":\n%s' %
                                (env.docname, ErrorString(error)))
        return super(LinkedNotebookParser, self).parse(rawtext, document)



def setup(app):
    """Initialize Sphinx extension."""
    app.setup_extension('nbsphinx')
    app.add_source_parser('.nblink', LinkedNotebookParser)

    return {'version': __version__, 'parallel_read_safe': True}
