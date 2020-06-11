from pathlib import Path
import re
from fuzzywuzzy import fuzz
import heapq
from collections import namedtuple
from typing import Dict, Tuple, Set, FrozenSet
from math import log

ration = fuzz.ratio

DUMP = "Sonstiges/"

def normalize_filename(string):
    """Remove all non ASCII letters and non digits from a string and
    replace whitespaces with underscores keeping dots untouched"""
    string = umlaut_converter(string)
    segs = string.split(".")
    for i, seg in enumerate(segs):
        segs[i] = re.sub(r"[\s]", "_", segs[i])
        segs[i] = re.sub(r"[\W]", "", seg, flags=re.ASCII)
    return ".".join(segs)


def umlaut_converter(string):
    """Convert all umlauts to their equivalent digraphs"""
    return string.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")


def get_hierarchy(p: Path) -> Dict[Path, Tuple[FrozenSet[str], int]]:
    """
    returns:
        a dictionary that resolves each directory of p (and recursive subdirectories)
        and the corresponding keywords to its level in the hierarchy.
    """
    def get_hierarchy_helper(p: Path, level: int) -> Tuple[Set[str], Dict[Path, Tuple[FrozenSet[str], int]]]:
        """
        returns:
            first tuple element is a set of all the keywords corresponding to p
            second element is a dictionary that resolves all of p's keywords and it's
            name to the corresponding level in the hierarchy
        """
        dirs = {}
        keywords: Set[str] = set()
        for x in p.glob("*"):
            if x.name.startswith("."):
                continue
            if x.is_dir():
                dir_kw, substructure = get_hierarchy_helper(x, level + 1)
                dir_kw.update([normalize_filename(x.name)])
                dirs[x] = (frozenset(dir_kw), level)
                dirs.update(substructure)
            if x.name == "keywords.txt":
                keywords.update(map(
                    lambda line: line.lstrip().rstrip(), x.open().readlines()))
                keywords -= {""}
        return keywords, dirs
    return get_hierarchy_helper(p, 0)[1]


def rename_inside(p: Path, hierarchy):
    """ Traverse the file system starting at p and sort encountered files
    according to their best match against the provided hierarchy.
    """
    HeapEntry = namedtuple("HeapEntry", ["score", "path", "level"])
    for x in p.glob("*"):
        if x.is_file():
            n = x.name
            if n.startswith(".") or n.endswith(".py") or n == "keywords.txt":
                continue
            def set_new_name(p): return x.rename(Path(p) / new_name)
            new_name = normalize_filename(x.name)
            max_ = []
            for path, (keywords, level) in hierarchy.items():
                # print(keywords)
                m = max(fuzz.partial_token_set_ratio(x, new_name) * log(len(x)) * (level)
                        for x in keywords)
                heapq.heappush(max_, HeapEntry(m, path, level))
            largest = heapq.nlargest(1, max_)[0]
            if largest.score >= 400:
                x.rename(largest.path / new_name)
                print(
                    f"Sorted '{new_name}' to '{str(largest.path)}' - best match @ {largest.score:.1f} ")
            else:
                set_new_name(DUMP)
                bests = ", ".join(
                    f"<{x.path} @ {x.score}>" for x in heapq.nlargest(3, max_))
                print(
                    f"Couldn't sort '{new_name}' - best matches are: {bests}")
        elif x.is_dir():
            rename_inside(x, hierarchy)
        else:
            print(f"Couldn't handle '{x}'")


def sort_by_hierarchy(p):
    h = get_hierarchy(p)
    return rename_inside(p, h)


sort_by_hierarchy(Path("."))
