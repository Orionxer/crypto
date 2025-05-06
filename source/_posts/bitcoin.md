---
title: 比特币
categories:
  - default
tags:
  - default
banner_img: /images/default.jpg
index_img: /images/default.jpg
date: 2025-05-06 16:46:04
---

## 官网
## 白皮书
## 发行总量
> 精确的比特币的发行总量参考Bitcoin Wiki的[Controlled supply](https://en.bitcoin.it/wiki/Controlled_supply)。

比特币自创世区块开始，每10分钟打包一次区块，每次打包产生50个比特币，并且每4年减半(暂时不考虑闰年)，则总量为
$$
S = 50 * 6 * 24 * 365 * 4 * (1+\frac{1}{2}+\frac{1}{4}+\frac{1}{8}+...+\frac{1}{2^n})
$$
把等比数列用$T$表示
$$
T=1+\frac{1}{2}+\frac{1}{4}+\frac{1}{8}+...+\frac{1}{2^n}
$$
则将$T$除以2可得
$$
\frac{T}{2}=\frac{1}{2}+\frac{1}{4}+\frac{1}{8}+...+\frac{1}{2^n}+\frac{1}{2^{n+1}}
$$
两式相减
$$
T-\frac{T}{2} = 1 + \frac{1}{2^{n+1}}
$$
因为数列收敛的特性，$\frac{1}{2^{n+1}}$忽略，则
$$
T \approx 2
$$
带入第一个公式
$$
S = 50 * 6 * 24 * 365 * 4 * (2) = 21,024,000
$$
粗略计算可得2100万个比特币。
