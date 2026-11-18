# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import particle as mod  # noqa: E402


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


# ===== v2 契约测试：初始全部失败，实现后必须通过 =====


def test_lifecycle_recycles_and_slot_reusable():
    pool = particle.make_pool(3)
    assert particle.spawn_particle(pool, {"life": 1.0, "vel": (0.5, 0.0)})["ok"] is True
    for _ in range(4):
        particle.step_life(pool, 0.4)
    snap = particle.snapshot(pool)
    assert all(not p["alive"] for p in snap)
    p2 = particle.spawn_particle(pool, {"life": 2.0, "vel": (0.0, 0.0)})
    assert p2["ok"] is True
    assert p2["age"] == 0.0


def test_recycle_counts():
    pool = particle.make_pool(4)
    for _ in range(4):
        particle.spawn_particle(pool, {"life": 0.8, "vel": (0.0, 0.0)})
    particle.step_life(pool, 1.0)
    assert particle.recycle_all_expired(pool) == 4
    assert sum(1 for p in particle.snapshot(pool) if p["alive"]) == 0


def test_budgeted_equals_full():
    def mk():
        pool = particle.make_pool(5)
        for _ in range(5):
            particle.spawn_particle(pool, {"life": 10.0, "vel": (0.3, -0.2)})
        return pool
    a, b = mk(), mk()
    for _ in range(6):
        particle.step_life(a, 0.1)
    guard = 0
    while True:
        r = particle.step_budgeted(b, 0.1, 2)
        guard += 1
        if r["done"] or guard > 20:
            break
    assert [(p["x"], p["y"]) for p in particle.snapshot(a)] ==            [(p["x"], p["y"]) for p in particle.snapshot(b)]
