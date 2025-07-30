from autoroutes import Routes
from timeit import timeit, default_timer
import fmt

router = Routes()
start = default_timer()
TOTAL_ROUTES = 10000
for i in range(TOTAL_ROUTES):
    router.add(f"/inc/{i}", method="GET", handler=lambda: i)
elapsed_t = default_timer() - start
fmt.print_time(f"[autoroutes] load {TOTAL_ROUTES} routes", elapsed_t)

for n in [0, 1000, 1500, 3000]:
    path = f"/inc/{n}"
    total = timeit(f"router.match('{path}')", globals=globals(), number=100000)
    fmt.print_time(f"[autoroutes] find path: {path}", total)

middle_path = f"/inc/{TOTAL_ROUTES // 2}"
total = timeit(
    f"router.match('{middle_path}')", globals=globals(), number=100000
)
fmt.print_time(f"[autoroutes] middle path {middle_path}", total)

total = timeit("router.match('/notfound')", globals=globals(), number=100000)
fmt.print_time("[autoroutes] unknown path", total)
