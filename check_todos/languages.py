from tree_sitter import Language


def import_language(extension):
    langs = {
        '.py': import_py_language,
        '.html': import_html_language,
        '.ts': import_ts_language,
        '.tsx': import_tsx_language,
        # TODO: check for shebang if missing suffix
        '': ...,
    }

    try:
        return langs[extension]()
    except KeyError:
        raise LanguageNotFoundError(extension)


def import_py_language():
    import tree_sitter_python

    return Language(tree_sitter_python.language())


def import_html_language():
    import tree_sitter_html

    return Language(tree_sitter_html.language())


def import_ts_language():
    import tree_sitter_typescript

    return Language(tree_sitter_typescript.language_typescript())


def import_tsx_language():
    import tree_sitter_typescript

    return Language(tree_sitter_typescript.language_tsx())


class LanguageNotFoundError(KeyError):
    def __init__(self, extension):
        self.extension = extension
        super().__init__(f'Unknown file extension: "{self.extension}"')
