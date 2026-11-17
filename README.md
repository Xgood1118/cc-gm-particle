# 粒子池与深度排序

一个用固定池管理粒子、并按深度正确排序的粒子系统。只用 Python 标准库。

## 保留签名

- `Particle`（dataclass：`slot, life, depth, order=0, alpha=1.0`）
- `Pool`
- `spawn(pool, spec)`
- `step(pool, dt)`
- `sort_by_depth(particles)`

模块级 `spawn` / `step` 是 `Pool` 同名方法的委托；`spec` 需含 `life`、`depth`，可选 `alpha`（默认 1.0）。

## 池规则

- 容量固定（`Pool(capacity)`，`capacity` 必须为正整数，否则 `ValueError`）。任何时刻 `pool.active <= pool.capacity`。
- 申请与回收成对：`spawn` 占用一个槽位；`step(dt)` 中寿命耗尽的粒子自动回收，槽位归还空闲栈。
- **槽位复用规则**：空闲槽位构成一个栈，初始 0 号在栈顶（首次申请依次拿 0,1,2,…）；回收的槽位压回栈顶，下一次申请优先拿到**最近回收**的槽位（LIFO）。回收后再申请拿到同一槽位，`pool.reused` 计数 +1。
- **池满行为**：`spawn` 返回 `None`，`pool.rejected` 计数 +1。不静默丢弃（调用方能拿到明确的 `None`），也不越界写（活跃数与槽位数组均不越界）。
- 计数器：`active`（当前活跃）、`peak`（峰值活跃）、`reused`（复用次数）、`rejected`（满池拒绝次数）。

## 排序规则

`sort_by_depth(particles)` 返回新列表，排序键为 `(是否半透明, 深度, 生成序号)`：

- 不透明粒子先绘制，半透明粒子（`alpha < 1.0`）后绘制；
- 组内按深度升序；
- 同深度按生成序号（`order`）保持生成顺序，重复排序结果不变（稳定）。

## 边界行为

- 粒子数为 0：`step` 返回空回收列表，`sort_by_depth([])` 返回 `[]`；
- 粒子数为 1：排序原样返回；
- 恰好满池：`active == capacity`，再次 `spawn` 返回 `None`。

## 抽样结果

`python -m particle.cli data/emitters.json --frames 60 --out sample.json`
（池容量 16，每帧每发射器发射 `count` 个粒子，寿命 `1/rate` 秒，dt = 1/60 s）

- 峰值活跃数 `peak_active`：**16**（= 容量，未越界）
- 复用次数 `reused`：**16**
- 满池拒绝次数 `rejected`：**268**
- 排序前后顺序差异 `order_diff`：**12**（16 个槽位中 12 个位置发生变化；同深度下排序按生成序号而非槽位号，槽位因 LIFO 复用与生成顺序不一致，故产生差异）
- 确定性：同样输入运行两次，`sample.json` 逐字节一致（模拟无随机源）。

## 自测

```
python -m pytest tests -q
python -m particle.cli data/emitters.json --frames 60 --out sample.json
```

测试覆盖：活跃数不超容量、申请/回收成对、回收复用槽位、稳定排序（同深度保序、半透明后绘制、结果可验证）、满池返回 `None`、空池/单粒子/恰好满池边界、两次运行结果一致。
