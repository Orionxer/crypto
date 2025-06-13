---
title: 问题汇总
categories:
  - default
tags:
  - default
banner_img: /images/default.jpg
index_img: /images/default.jpg
date: 2025-06-12 16:38:01
---

- [x] Phantom Wallet授权gmgn.ai的正确方式：点击登录之后，选择`连接插件钱包交易`，选择`Phantom`授权即可正确同步地址余额
  - ![alt text](gmgn_login_1.png)
  - ![alt text](gmgn_login_2.png)
- [ ] Phantom Wallet无法授权[gmgn](https://gmgn.ai)以及[axiom](https://axiom.trade)，但是可以授权[opensea](https://opensea.io)
  - Phantom wallet弹出的授权信息的Solana地址是正确的，但是授权后，gmgn以及axiom显示的地址已经变化了
  - 如果是okx wallet授权登录gmgn则可以正常显示余额
- [ ] 波场网络转账交易所地址手续费高的问题
  - [ ] 交易所的收款地址是合约地址，不是普通地址，因此可能会多收手续费。[动态能量模型介绍](https://support.tronlink.org/hc/zh-cn/articles/14496201625113)
  - [x] 发送TRX[租用能量](https://trxjt.com/)，租借一次最多是65000，租多了没用
  - [ ] 交易所购买TRX没用，即便是交易所的收款地址有USDT。以下是转账提示
  - ![双倍能量](energy.png)
