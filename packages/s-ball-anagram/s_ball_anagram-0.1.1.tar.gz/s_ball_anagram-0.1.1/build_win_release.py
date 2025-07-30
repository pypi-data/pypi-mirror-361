import argparse
from typing import Sequence
import subprocess
import sys

try:
    import s_ball_anagram.__about__
except ImportError:
    print('s-ball-anagram package must already be installed')
    s_ball_anagram = None
    exit(1)


NAME = 'anagrams'
DEFMODE = 'onefile'


def parse_command_line(argv: Sequence[str], version: str) -> tuple[argparse.Namespace, list[str]]:
    """Parse a command line and provide sensible defaults"""

    parser = argparse.ArgumentParser(
        prog='anagrams',
        description='Builds a Windows release onefile using nuitka',

    )
    parser.add_argument('--mode', action='store')
    parser.add_argument('--onefile', action='store_const', const='onefile', dest='mode')
    parser.add_argument('--standalone', action='store_const', const='standalone', dest='mode')
    parser.add_argument('--file-version', default=version)
    parser.add_argument('--product-version', default=version)
    parser.add_argument('--file-description',
                        default='Build anagrams using a French dictionary')
    parser.add_argument('--copyright',
                        default='Copyright s-ball - 2025-current - MIT License')
    parser.add_argument('--onefile-tempdir-spec', dest='"one_temp"')
    parser.add_argument('--output-filename', default='anagrams.exe')
    return parser.parse_known_args(argv)


def build_params(argv: Sequence[str]) -> list[str]:
    """Main procedure"""
    # we should be able to launch:
    # nuitka --onefile --onefile-tempdir-spec="{CACHE_DIR}/s-ball/anagrams" --python-flag="-m" --output-filename=anagrams.exe --include-data-files="c:\Users\serge\PycharmProjects\s-ball-anagram\venv\share\dict\dict-fr-AU-DELA-common-words.ascii=share/dict/" src/s_ball_anagram
    params = ['python', '-m', 'nuitka', '--python-flag="-m"',
              f'--include-data-files="{sys.prefix}/share/dict/dict-fr-AU-DELA-common-words.ascii=share/dict/"',]
    cmdline: argparse.Namespace
    cmdline, extra = parse_command_line(argv, s_ball_anagram.__about__.__version__)

    if 'mode' in cmdline and cmdline.mode is not None:
        mode = cmdline.mode
    else:
        mode = DEFMODE
    if mode == 'onefile':
        if 'one_temp' in cmdline and cmdline.one_temp is not None:
            one_temp = cmdline.one_temp
        else:
            one_temp = '"{CACHE_DIR}/s-ball/anagrams"'
        params.extend(['--onefile', f'--onefile-tempdir-spec={one_temp}'])
    else:
        params.append('--standalone')

    for p in ('file-version', 'product-version', 'file-description',
              'copyright', 'output-filename'):
        params.append(f'--{p}="{getattr(cmdline, p.replace("-", "_"))}"')

    params.extend(extra)
    params.append('src/s_ball_anagram')

    return params


def main(argv):
    print(sys.executable, sys.prefix)
    params = build_params(argv)
    print(params)
    print(' '.join(params))
    if sys.platform.startswith('win32'):
        cp = subprocess.run(' '.join(params), executable=sys.executable)
    else:
        cp = subprocess.run(params, executable=sys.executable)
    return cp.returncode


if __name__ == '__main__':
    exit(main(sys.argv[1:]))