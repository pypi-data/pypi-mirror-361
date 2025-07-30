from itertools import permutations as pr
from dataclasses import dataclass
from pathlib import Path
import sys


ref = None


@dataclass
class Jardin:
    mot: str

    def search(self, hint: str, refs):
        ln = len(hint)
        for t in sorted(set(pr(self.mot, ln))):
            if refs and (t not in refs):
                continue
            for i, c in enumerate(hint):
                if c != '_' and c != t[i]:
                    break
            else:
                yield t

    def process(self):
        while True:
            hint = input('A rechercher (_ pour une position vide. Exemple _A_) : ')
            hint = hint.strip().upper()
            x = hint.split()
            if len(x) == 0:
                break
            if len(x) == 2 and x[1].upper() == 'X':
                r = None
            else:
                r = ref
            hint = x[0]
            if len(hint) == 0:
                break
            for i in self.search(hint, r):
                print(''.join(i))


def main():
    global ref
    d = Path(sys.prefix)/'share'/'dict'
    try:
        ref = set(tuple(w.strip().upper()) for w in
                  open(d/'dict-fr-AU-DELA-common-words.ascii'))
    except OSError:
        print(f'Dossier dictionnaire vide : {d}')
        ref = None
    while True:
        mot = input('Lettres : ')
        mot = mot.upper().strip()
        if len(mot) == 0:
            break
        j = Jardin(mot)
        j.process()
