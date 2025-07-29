
from collections.abc import MutableMapping
from itertools import zip_longest
from typing import Optional

from dough.common import util


def flatten(d: dict, parent_key: Optional[str] = "", sep: Optional[str] = ".") -> dict:
    """Flattens nested dictionaries into a single dictionary with concatenated keys.

    Args:
        d (dict): The dictionary to flatten.
        parent_key (Optional[str]): The base key to prepend to each key in the nested dictionary.
        sep (Optional[str]): The separator to use between keys.

    Returns:
        dict: A new dictionary with flattened keys and values.

    Example:
        >>> flatten({'a': {'b': {'c': 1}}})
        {'a.b.c': 1}
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(util.flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def list_flatter(list_org: list) -> list:
    """Converts a list of lists into a single flat list.

    Args:
        list_org (list): The original nested list.

    Returns:
        list: A flat list containing all elements from the nested lists.

    Example:
        >>> list_flatter([[1, 2], [3, 4]])
        [1, 2, 3, 4]
    """
    list_flatted = []
    for sublist in list_org:
        for item in sublist:
            list_flatted.append(item)
    return list_flatted


def chunk(iterable, n, fillvalue=None):
    """Splits an iterable into chunks of a specified size, filling up with a fill value if necessary.

    Args:
        iterable: The iterable to split.
        n (int): The number of elements in each chunk.
        fillvalue: The value to use to fill incomplete chunks.

    Returns:
        list: A list of chunks, each of which is a list containing up to `n` elements.

    Example:
        >>> chunk([1, 2, 3, 4, 5], 2)
        [[1, 2], [3, 4], [5]]
    """
    return [list(item) for item in list(zip_longest(*[iter(iterable)] * n, fillvalue=fillvalue))]

