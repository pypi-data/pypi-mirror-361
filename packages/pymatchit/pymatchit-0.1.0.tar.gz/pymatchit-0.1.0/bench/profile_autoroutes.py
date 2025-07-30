import pstats
from cProfile import runctx

from autoroutes import Routes

router = Routes()
TOTAL_ROUTES = 10000
for i in range(TOTAL_ROUTES):
    router.add(f"/inc/{i}", method="GET", handler=lambda: i)

runctx(
    f'for i in range(100000):\n router.match("/inc/{TOTAL_ROUTES // 2}")',
    globals(),
    locals(),
    "profile.prof",
)

s = pstats.Stats("profile.prof")
s.strip_dirs().sort_stats("time").print_stats()
