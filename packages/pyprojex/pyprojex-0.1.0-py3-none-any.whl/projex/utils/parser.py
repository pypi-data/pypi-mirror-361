# custom parser
# because argparse is not flexible
import sys
from sys import argv
from log import setup_logging
from typing import List, Dict, Generator, Union

log = setup_logging()

allowed_actions = [
    "run",
]

class Parsed:
    parsed = {}
    def __getattr__(self, item):
        return self.parsed[item]

    def __str__(self):
        return f' | '.join([f'{i} -> {j}' for i,j in self.parsed.items()])


def find_flags(lst: List[str]) -> Parsed:
    """
    This function will find --flag value in the list of argv given.
    Parameters:
        lst (List[str]): List of sys.argv
    Returns:
        Parsed: Flag:Value class
    """
    parsed = {
        'raw': []
    }
    to_load = False
    for i in range(1, len(lst)):
        if not lst[i].startswith('-') and to_load and to_load != 'raw': # while using flag to set a value
            parsed[to_load.lstrip('-')] = lst[i]
            to_load = False
        elif lst[i].startswith('-') and not to_load: # setting to load for flag
            to_load = lst[i]
        elif lst[i].startswith('-') and to_load: # if there is to load and but new flag is here, so last one is indicator
            parsed[to_load.lstrip('-')] = True
            to_load = lst[i]
        elif not lst[i].startswith('-') and not to_load: # raw value without flags maybe i make positionals strictly first
            parsed['raw'].append(lst[i])
    if to_load:
        parsed[to_load.lstrip('-')] = True
    res = Parsed()
    res.parsed = parsed
    return res


def parse():
    if not len(argv)-1:
        log.critical('usage choc <action>')
    return find_flags(sys.argv)
