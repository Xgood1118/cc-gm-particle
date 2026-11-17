# -*- coding: utf-8 -*-
"""命令行入口：跑固定帧数模拟，输出统计与排序前后顺序到 JSON。

每个发射器每帧发射 count 个粒子，寿命取 1/rate 秒，深度取 depth。
模拟无随机源，同样输入两次运行结果完全一致。
"""
import argparse
import json

import particle as m

DT = 1.0 / 60.0
CAPACITY = 16


def run(emitters, frames, capacity=CAPACITY, dt=DT):
    pool = m.Pool(capacity)
    for _ in range(frames):
        for e in emitters:
            spec = {
                "life": 1.0 / float(e["rate"]),
                "depth": float(e["depth"]),
                "alpha": float(e.get("alpha", 1.0)),
            }
            for _ in range(int(e["count"])):
                m.spawn(pool, spec)
        m.step(pool, dt)
    alive = pool.particles
    before = [p.slot for p in alive]
    after = [p.slot for p in m.sort_by_depth(alive)]
    return {
        "frames": frames,
        "capacity": pool.capacity,
        "active": pool.active,
        "peak_active": pool.peak,
        "reused": pool.reused,
        "rejected": pool.rejected,
        "order_before": before,
        "order_after": after,
        "order_diff": sum(1 for a, b in zip(before, after) if a != b),
    }


def main():
    ap = argparse.ArgumentParser(description="粒子池与深度排序")
    ap.add_argument("emitters", help="发射器配置 JSON 路径")
    ap.add_argument("--frames", type=int, default=60)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    with open(a.emitters, encoding="utf-8") as f:
        emitters = json.load(f)
    result = run(emitters, a.frames)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
