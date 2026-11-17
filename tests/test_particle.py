# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import particle as mod  # noqa: E402
particle = mod

def read_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def read_hex(path):
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def test_pool_capacity():
    pool = particle.Pool(8)
    assert pool.capacity == 8
    n = 0
    for _ in range(20):
        if pool.spawn({"life": 1.0, "depth": 0.1}):
            n += 1
    assert n <= 8


def test_sort_stable():
    ps = [particle.Particle(0, 1.0, 0.5), particle.Particle(1, 1.0, 0.5)]
    out = particle.sort_by_depth(ps)
    assert [p.slot for p in out] == [0, 1]
