# -*- coding: utf-8 -*-
"""粒子池与深度排序"""

from dataclasses import dataclass


@dataclass
class Particle:
    """一个粒子。"""
    slot: int
    life: float
    depth: float
    order: int = 0




class Pool:

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Pool 尚未实现")


def spawn(pool, spec):
    """申请粒子"""
    raise NotImplementedError("spawn 尚未实现")


def step(pool, dt):
    """推进一帧"""
    raise NotImplementedError("step 尚未实现")


def sort_by_depth(particles):
    """按深度稳定排序"""
    raise NotImplementedError("sort_by_depth 尚未实现")



def make_pool(capacity):
    """建立粒子池：返回 dict(capacity, items=[]) 形态的池对象。"""
    raise NotImplementedError("make_pool 尚未实现")


def spawn_particle(pool, spec):
    """生成一个粒子：返回 dict(id, ok, x, y, age, life)。"""
    raise NotImplementedError("spawn_particle 尚未实现")


def step_life(pool, dt):
    """带寿命步进：返回 dict(alive, recycled)。"""
    raise NotImplementedError("step_life 尚未实现")


def recycle_all_expired(pool):
    """回收全部到期粒子：返回回收数量。"""
    raise NotImplementedError("recycle_all_expired 尚未实现")


def snapshot(pool):
    """返回当前粒子快照：list(dict(id, x, y, age, alive))。"""
    raise NotImplementedError("snapshot 尚未实现")


def step_budgeted(pool, dt, budget):
    """预算化步进：返回 dict(updated, done)。"""
    raise NotImplementedError("step_budgeted 尚未实现")
