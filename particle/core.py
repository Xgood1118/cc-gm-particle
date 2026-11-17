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


def spawn(pool, spec):
    """申请粒子"""
    raise NotImplementedError("spawn 尚未实现")


def step(pool, dt):
    """推进一帧"""
    raise NotImplementedError("step 尚未实现")


def sort_by_depth(particles):
    """按深度稳定排序"""
    raise NotImplementedError("sort_by_depth 尚未实现")


class Pool:
    """class"""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Pool 尚未实现")

