RESET = '\033[0m'


def red(s):
    return f'\033[31m{s}{RESET}'


def green(s):
    return f'\033[32m{s}{RESET}'


def red_bold(s: str) -> str:
    return f'\033[1m\033[31m{s}{RESET}'


def blue(s):
    return f'\033[34m{s}{RESET}'
