from typing import Callable, TypedDict
from pymatchit import PyRouter
from timeit import default_timer, timeit

import fmt

class RouteData(TypedDict):
    method: str
    handler: Callable[..., int]


RouterClass = PyRouter[RouteData]
router = RouterClass()
start = default_timer()
TOTAL_ROUTES = 10000
for i in range(TOTAL_ROUTES):
    router.insert(f"/inc/{i}", {"method": "GET", "handler": lambda: i})

elapsed_t = default_timer() - start
fmt.print_time(f"[pymatchit] load {TOTAL_ROUTES} routes", elapsed_t)

for n in [0, 1000, 1500, 3000]:
    path = f"/inc/{n}"
    total = timeit(f"router.at('{path}')", globals=globals(), number=100000)
    fmt.print_time(f"[pymatchit] find path: {path}", total)

middle_path = f"/inc/{TOTAL_ROUTES // 2}"
total = timeit(
    f"router.at('{middle_path}')", globals=globals(), number=100000
)
fmt.print_time(f"[pymatchit] middle path {middle_path}", total)

code = """
try:
    router.at('/notfound')
except KeyError:
    pass
"""
total = timeit(code, globals=globals(), number=100000)
fmt.print_time("[pymatchit] unknown path", total)
