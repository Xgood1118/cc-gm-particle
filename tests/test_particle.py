# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import particle as mod  # noqa: E402
from particle.cli import run  # noqa: E402

particle = mod

SPEC = {"life": 1.0, "depth": 0.1}


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


# --- 池：活跃数不超容量 ---

def test_active_never_exceeds_capacity():
    pool = particle.Pool(4)
    for _ in range(10):
        particle.spawn(pool, dict(SPEC))
        assert pool.active <= pool.capacity
        assert len(pool.particles) <= pool.capacity
    assert pool.active == 4


def test_spawn_recycle_paired():
    pool = particle.Pool(3)
    for _ in range(3):
        particle.spawn(pool, dict(SPEC))
    particle.step(pool, 0.5)   # 未到期，不回收
    assert pool.active == 3
    particle.step(pool, 0.6)   # 全部到期回收
    assert pool.active == 0
    assert pool.particles == []


# --- 池：回收后复用同一槽位 ---

def test_recycled_slot_reused():
    pool = particle.Pool(2)
    a = particle.spawn(pool, dict(SPEC))
    b = particle.spawn(pool, dict(SPEC))
    particle.step(pool, 1.0)   # 两个都回收
    c = particle.spawn(pool, dict(SPEC))
    d = particle.spawn(pool, dict(SPEC))
    # 回收顺序 a 先 b 后，b 的槽位在栈顶，先被复用
    assert c.slot == b.slot
    assert d.slot == a.slot
    assert pool.reused == 2


# --- 排序：稳定 + 半透明后绘制 ---

def test_sort_by_depth_order():
    ps = [
        particle.Particle(0, 1.0, 0.9, order=0),
        particle.Particle(1, 1.0, 0.1, order=1),
        particle.Particle(2, 1.0, 0.5, order=2),
    ]
    out = particle.sort_by_depth(ps)
    assert [p.slot for p in out] == [1, 2, 0]


def test_sort_same_depth_keeps_spawn_order():
    ps = [particle.Particle(i, 1.0, 0.5, order=i) for i in range(5)]
    for _ in range(3):  # 重复排序结果不变
        out = particle.sort_by_depth(ps)
        assert [p.order for p in out] == [0, 1, 2, 3, 4]


def test_sort_translucent_last():
    ps = [
        particle.Particle(0, 1.0, 0.1, order=0, alpha=0.5),  # 半透明但深度小
        particle.Particle(1, 1.0, 0.9, order=1),             # 不透明但深度大
    ]
    out = particle.sort_by_depth(ps)
    assert [p.slot for p in out] == [1, 0]


def test_sort_result_verifiable():
    pool = particle.Pool(8)
    for d in (0.7, 0.2, 0.2, 0.9):
        particle.spawn(pool, {"life": 1.0, "depth": d})
    out = particle.sort_by_depth(pool.particles)
    keys = [(p.translucent, p.depth, p.order) for p in out]
    assert keys == sorted(keys)


# --- 边界：满池 ---

def test_full_pool_spawn_returns_none():
    pool = particle.Pool(2)
    assert particle.spawn(pool, dict(SPEC)) is not None
    assert particle.spawn(pool, dict(SPEC)) is not None
    assert particle.spawn(pool, dict(SPEC)) is None
    assert pool.rejected == 1
    assert pool.active == 2  # 不越界写


def test_exactly_full_pool():
    pool = particle.Pool(3)
    for _ in range(3):
        assert particle.spawn(pool, dict(SPEC)) is not None
    assert pool.active == 3 == pool.capacity
    assert pool.peak == 3
    assert particle.spawn(pool, dict(SPEC)) is None


# --- 边界：0 与 1 个粒子 ---

def test_empty_pool():
    pool = particle.Pool(4)
    assert particle.step(pool, 1.0) == []
    assert pool.active == 0
    assert particle.sort_by_depth(pool.particles) == []


def test_single_particle():
    pool = particle.Pool(4)
    p = particle.spawn(pool, dict(SPEC))
    assert pool.active == 1
    assert particle.sort_by_depth(pool.particles) == [p]
    particle.step(pool, 2.0)
    assert pool.active == 0


def test_zero_capacity_rejected():
    try:
        particle.Pool(0)
    except ValueError:
        pass
    else:
        raise AssertionError("容量为 0 应抛 ValueError")


# --- 输出：确定性 ---

def test_run_deterministic():
    emitters = [{"count": 5, "rate": 2.0, "depth": 0.3}]
    r1 = run(emitters, 60)
    r2 = run(emitters, 60)
    assert r1 == r2
    assert r1["peak_active"] <= r1["capacity"]
