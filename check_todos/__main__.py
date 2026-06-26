import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal

from tree_sitter import Parser, Query, QueryCursor

from check_todos.languages import import_language
from check_todos.rich import blue, green, red, red_bold


@dataclass
class TODOComment:
    text: str
    relative_path: str
    line_no: int  # TODO: more stuff
    context: list[tuple[int, str]]
    issue: str | None = None
    tag: Literal['todo', 'fixme'] = 'todo'


@lru_cache
def comment_parser(extension):
    lang = import_language(extension)
    parser = Parser(lang)
    query = Query(lang, '(comment) @comments')
    return query, parser


def iter_todos(glob, prefix):
    if prefix:
        pattern = f'{args.prefix}-\\d'
    else:
        pattern = r'[A-Z]+-\d+'

    paths = list(Path().glob(glob))

    if not len(paths):
        raise RuntimeError(f'Nothing found in: {glob}')

    for path in paths:
        if not path.is_file():
            continue

        query, parser = comment_parser(path.suffix)
        raw_source = path.read_bytes()
        tree = parser.parse(raw_source)
        query_cursor = QueryCursor(query)
        captures = query_cursor.captures(tree.root_node)
        source_lines = [
            (idx + 1, line) for idx, line in enumerate(raw_source.decode().splitlines())
        ]

        for comment_node in captures.get('comments', []):
            comment = comment_node.text.decode().strip()
            start_line_no = comment_node.start_point[0]
            end_line_no = comment_node.end_point[0]
            start_col = comment_node.start_point[1]
            end_col = comment_node.end_point[1]

            is_todo, is_fixme = 'TODO' in comment, 'FIXME' in comment
            if is_todo or is_fixme:
                context = []
                for no, line in source_lines[
                    max(0, start_line_no - 2) : end_line_no + 3
                ]:
                    context.append((no, line))
                    if no == start_line_no + 1:
                        context.append(
                            (None, ' ' * start_col + red('^' * (end_col - start_col)))
                        )

                todo = TODOComment(
                    text=comment,
                    relative_path=str(path),
                    line_no=comment_node.start_point[0],
                    context=context,
                    tag='todo' if is_todo else 'fixme',
                )
                match = re.search(pattern, todo.text)
                if match:
                    todo.issue = match.group()

                yield todo


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'path',
        nargs='+',
        help='glob of source code files to search for TODOs in',
    )
    parser.add_argument(
        '--output',
        '-o',
        choices=('summary', 'jsonl'),
        default='summary',
        help='Output report format',
    )
    parser.add_argument(
        '--prefix',
        nargs='*',
        help='Optional issue ID prefix.',
    )
    args = parser.parse_args()

    untracked_todos, tracked_todos = [], []
    for glob in args.path:
        for todo in iter_todos(glob, args.prefix):
            if todo.issue:
                tracked_todos.append(todo)
            else:
                untracked_todos.append(todo)

    match args.output:
        case 'summary':
            if untracked_todos:
                for todo in untracked_todos:
                    print()
                    print(
                        '  ',
                        blue('--->'),
                        f'{todo.relative_path}:{todo.line_no}',
                    )
                    print('       ', blue(' |'))
                    for line_no, line in todo.context:
                        line_number = f'{line_no:4d}' if line_no else '    '
                        print('    ', blue(f'{line_number}|'), line)
                    print('       ', blue(' |'))
                print()

                print(red_bold(f'{len(untracked_todos)} untracked todos found'))
                sys.exit(1)

            elif tracked_todos:
                print(green(f'{len(tracked_todos)} tracked todos'))

            else:
                print('no todos')
        case 'jsonl':
            for todo in untracked_todos + tracked_todos:
                print(json.dumps(asdict(todo)))


if __name__ == '__main__':
    main()
