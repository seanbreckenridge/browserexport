from collections import Counter
from typing import List
from pprint import pprint

from urllib.parse import urlsplit

from .model import Visit


def demo_visit(visits: List[Visit]) -> None:
    print("Demo: Your most common sites....")
    pprint(Counter(map(lambda v: urlsplit(v.url).netloc, visits)).most_common(10))
