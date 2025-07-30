import pstats
from cProfile import runctx
from timeit import timeit
from typing import Callable, TypedDict

from pymatchit import PyRouter


class RouteData(TypedDict):
    method: str
    handler: Callable[..., int]


RouterClass = PyRouter[RouteData]
router = RouterClass()
TOTAL_ROUTES = 10000
for i in range(TOTAL_ROUTES):
    router.insert(f"/inc/{i}", {"method": "GET", "handler": lambda: i})

runctx(
    f'for i in range(100000):\n router.at("/inc/{TOTAL_ROUTES // 2}")',
    globals(),
    locals(),
    "profile.prof",
)

s = pstats.Stats("profile.prof")
s.strip_dirs().sort_stats("time").print_stats()
