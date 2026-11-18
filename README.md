# 粒子池与深度排序

一个用固定池管理粒子、并按深度正确排序的粒子系统

## 保留签名

- `Particle`
- `Pool`
- `spawn(pool, spec)`
- `step(pool, dt)`
- `sort_by_depth(particles)`

## 自测

```
python -m pytest tests -q
python -m particle.cli data/emitters.json --frames 60 --out sample.json
```
