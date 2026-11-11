"""Select a maximum-score set of non-overlapping candidate clip windows."""
from bisect import bisect_right
from dataclasses import asdict, dataclass
from pathlib import Path
import argparse
import json


@dataclass(frozen=True)
class Window:
    id: str
    start_ms: int
    end_ms: int
    score: int

    def __post_init__(self):
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError('Window id must be a nonempty string')
        if any(type(x) is not int for x in (self.start_ms, self.end_ms, self.score)):
            raise ValueError('Times and scores must be integers')
        if not 0 <= self.start_ms < self.end_ms:
            raise ValueError('Window must have a nonnegative start and positive duration')


def select(windows, *, limit=None, gap_ms=0):
    """Maximize total score; ties skip the last candidate in end-time order.

    Intervals are half open. A candidate can begin exactly when its predecessor
    ends plus gap_ms. Negative-score candidates may be skipped.
    """
    if type(gap_ms) is not int or gap_ms < 0:
        raise ValueError('gap_ms must be a nonnegative integer')
    if limit is not None and (type(limit) is not int or limit < 0):
        raise ValueError('limit must be a nonnegative integer or None')
    ordered = sorted(windows, key=lambda w: (w.end_ms, w.start_ms, w.id))
    n = len(ordered)
    if len({w.id for w in ordered}) != n:
        raise ValueError('Window ids must be unique')
    ends = [w.end_ms for w in ordered]
    # Number of compatible windows in the prefix before candidate i.
    prefixes = [bisect_right(ends, w.start_ms-gap_ms, hi=i) for i,w in enumerate(ordered)]

    if limit is None or limit >= n:
        best = [0] * (n+1)
        take = bytearray(n+1)
        for i,w in enumerate(ordered,1):
            value = w.score + best[prefixes[i-1]]
            if value > best[i-1]:
                best[i], take[i] = value, 1
            else:
                best[i] = best[i-1]
        chosen = []
        i = n
        while i:
            if take[i]:
                chosen.append(ordered[i-1]); i = prefixes[i-1]
            else:
                i -= 1
        return tuple(reversed(chosen))

    previous = [0] * (n+1)
    choices = [bytearray()]
    for _ in range(limit):
        current = [0] * (n+1)
        take = bytearray(n+1)
        for i,w in enumerate(ordered,1):
            value = w.score + previous[prefixes[i-1]]
            if value > current[i-1]:
                current[i], take[i] = value, 1
            else:
                current[i] = current[i-1]
        choices.append(take)
        previous = current
    i,k = n,limit
    chosen = []
    while i and k:
        if choices[k][i]:
            chosen.append(ordered[i-1]); i = prefixes[i-1]; k -= 1
        else:
            i -= 1
    return tuple(reversed(chosen))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('windows', type=Path, help='JSON array of candidate windows')
    parser.add_argument('--limit', type=int)
    parser.add_argument('--gap-ms', type=int, default=0)
    args = parser.parse_args()
    try:
        data = json.loads(args.windows.read_text(encoding='utf-8'))
        if not isinstance(data,list):
            raise ValueError('Expected a JSON array')
        chosen = select((Window(**row) for row in data), limit=args.limit, gap_ms=args.gap_ms)
    except (ValueError, TypeError, OSError) as error:
        parser.error(str(error))
    print(json.dumps({'score':sum(w.score for w in chosen),'selected':[asdict(w) for w in chosen]},indent=2))


if __name__ == '__main__':
    main()
