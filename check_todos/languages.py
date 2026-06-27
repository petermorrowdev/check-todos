import importlib
from dataclasses import dataclass

from tree_sitter import Language


def import_language(extension):
    for lang in LANGUAGES:
        if lang.extension == extension:
            mod = importlib.import_module(lang.module)
            lang_func = getattr(mod, lang.function)
            return Language(lang_func())

    raise LanguageNotFoundError(extension)


@dataclass
class Lang:
    extension: str
    module: str
    function: str = 'language'


LANGUAGES = [
    Lang('.html', 'tree_sitter_html'),
    Lang('.py', 'tree_sitter_python'),
    Lang('.toml', 'tree_sitter_toml'),
    Lang('.ts', 'tree_sitter_typescript', 'language_typescript'),
    Lang('.tsx', 'tree_sitter_typescript', 'language_tsx'),
    Lang('.yaml', 'tree_sitter_yaml'),
]


class LanguageNotFoundError(KeyError):
    def __init__(self, extension):
        self.extension = extension
        super().__init__(f'Unknown file extension: "{self.extension}"')
