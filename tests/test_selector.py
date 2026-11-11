from itertools import combinations
from random import Random
import unittest

from selector import Window, select


class SelectorTest(unittest.TestCase):
    def test_greedy_counterexample_and_exact_boundary(self):
        windows = [Window('whole',0,20,10), Window('left',0,10,6), Window('right',10,20,7)]
        self.assertEqual([x.id for x in select(windows)],['left','right'])
        self.assertEqual([x.id for x in select(windows,limit=1)],['whole'])
        self.assertEqual([x.id for x in select(windows,gap_ms=1)],['whole'])

    def test_dynamic_program_matches_brute_force(self):
        random=Random(42)
        for _ in range(30):
            windows=[]
            for i in range(8):
                start=random.randrange(20)
                windows.append(Window(str(i),start,start+random.randrange(1,9),random.randrange(-3,13)))
            for gap in (0,2):
                for limit in (None,0,1,3,8):
                    cap=len(windows) if limit is None else limit
                    brute=0
                    for k in range(cap+1):
                        for subset in combinations(windows,k):
                            ordered=sorted(subset,key=lambda w:w.start_ms)
                            if all(a.end_ms+gap<=b.start_ms for a,b in zip(ordered,ordered[1:])):
                                brute=max(brute,sum(x.score for x in subset))
                    chosen=select(windows,limit=limit,gap_ms=gap)
                    self.assertEqual(sum(x.score for x in chosen),brute)
                    self.assertLessEqual(len(chosen),cap)
                    self.assertTrue(all(a.end_ms+gap<=b.start_ms for a,b in zip(chosen,chosen[1:])))

    def test_same_score_ties_are_stable(self):
        a,b=Window('a',0,10,5),Window('b',0,10,5)
        self.assertEqual(select([b,a]),(a,))
        self.assertEqual(select([b,a],limit=1),(a,))

    def test_bad_input_is_rejected(self):
        with self.assertRaises(ValueError):Window('bad',10,10,5)
        with self.assertRaises(ValueError):select([],gap_ms=-1)
        with self.assertRaises(ValueError):select([Window('a',0,1,2),Window('a',1,2,3)])


if __name__ == '__main__':
    unittest.main()
