# -*- coding: utf-8 -*-
"""粒子池与深度排序。

池容量固定，槽位申请/回收成对；排序按深度稳定进行，半透明粒子后绘制。
"""

from dataclasses import dataclass


@dataclass
class Particle:
    """一个粒子。order 为生成序号，用于同深度时保持生成顺序。"""
    slot: int
    life: float
    depth: float
    order: int = 0
    alpha: float = 1.0

    @property
    def translucent(self):
        return self.alpha < 1.0


def spawn(pool, spec):
    """申请粒子。池满时返回 None（pool.rejected 计数 +1），不静默丢弃也不越界写。"""
    return pool.spawn(spec)


def step(pool, dt):
    """推进一帧：寿命递减，寿命结束的粒子自动回收。"""
    return pool.step(dt)


def sort_by_depth(particles):
    """按深度稳定排序：先不透明后半透明，组内按深度升序，同深度保持生成顺序。"""
    return sorted(particles, key=lambda p: (p.translucent, p.depth, p.order))


class Pool:
    """固定容量粒子池。

    槽位复用规则：空闲槽位构成一个栈，初始按编号升序排列（0 号在栈顶）；
    回收的槽位压回栈顶，下一次申请优先拿到最近回收的槽位。
    """

    def __init__(self, capacity):
        if not isinstance(capacity, int) or capacity <= 0:
            raise ValueError("capacity 必须是正整数")
        self.capacity = capacity
        self._slots = [None] * capacity
        self._free = list(reversed(range(capacity)))  # 栈顶是最小空槽号
        self._used_once = set()
        self._seq = 0
        self.active = 0      # 当前活跃数
        self.peak = 0        # 峰值活跃数
        self.reused = 0      # 槽位回收后再次被申请的次数
        self.rejected = 0    # 池满拒绝次数

    def spawn(self, spec):
        """申请一个槽位并放入粒子；池满返回 None。"""
        if not self._free:
            self.rejected += 1
            return None
        slot = self._free.pop()
        if slot in self._used_once:
            self.reused += 1
        else:
            self._used_once.add(slot)
        p = Particle(
            slot=slot,
            life=float(spec["life"]),
            depth=float(spec["depth"]),
            order=self._seq,
            alpha=float(spec.get("alpha", 1.0)),
        )
        self._seq += 1
        self._slots[slot] = p
        self.active += 1
        if self.active > self.peak:
            self.peak = self.active
        return p

    def step(self, dt):
        """推进 dt 秒，回收寿命结束的粒子，返回本帧回收的槽位列表。"""
        recycled = []
        for i, p in enumerate(self._slots):
            if p is None:
                continue
            p.life -= dt
            if p.life <= 0:
                self._slots[i] = None
                self._free.append(i)  # 压回栈顶，下次申请优先复用
                self.active -= 1
                recycled.append(i)
        return recycled

    @property
    def particles(self):
        """当前活跃粒子，按槽位号升序。"""
        return [p for p in self._slots if p is not None]
