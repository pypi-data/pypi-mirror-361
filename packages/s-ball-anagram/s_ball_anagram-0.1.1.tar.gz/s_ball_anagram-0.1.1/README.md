# s-ball-anagram

[![PyPI - Version](https://img.shields.io/pypi/v/s-ball-anagram.svg)](https://pypi.org/project/s-ball-anagram)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/s-ball-anagram.svg)](https://pypi.org/project/s-ball-anagram)

-----

## Table of Contents

- [Goal](#goal)
- [Status](#status)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Goal
This tool is intended to help solving anagrams in games like 
[Le jardin des mots](https://play.google.com/store/apps/details?id=com.iscoolentertainment.snc&hl=fr).
It can test permutations of a given set of letters against a *mask* containing
optionally some already in-place letters.

It is even possible to limit the permutations to known French words. They are then
searched in `dict-fr-AU-DELA`, a French dictionary from 
Laboratoire d'Automatique Documentaire et Linguistique (LADL).

## Status

I currently use the program, yet I declare it to only by beta quality because
it is still lacking extensive tests.

## Installation

```console
pip install s-ball-anagram
```

## Usage

After installation, the program `anagram` should be directly accessible,
so typing:

```commandline
anagram
```

should be enough.

Alternately, it can be launched as a Python module with:

```commandline
python -m s_ball_anagram
```

The letters from which the anagrams are to be found can be typed in
uppercase or lowercase.

Then the mask to be searched should be provided by using `_` for unknown
letters. For example to search 4 letters anagrams the second of which is a
`A`, one should type `_a__` or `_A__`.

## License

`s-ball-anagram` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
