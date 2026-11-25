# tiny-bot-beat-buy-and-hold

[![make.fun · u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1](https://make.fun/badge/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1.svg)](https://make.fun/bounty/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1?utm_source=github&utm_medium=readme&utm_campaign=u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1)
[![rank](https://make.fun/badge/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1/cryptokom-tech/tiny-bot-beat-buy-and-hold/rank.svg)](https://make.fun/bounty/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1)
[![reward](https://make.fun/badge/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1/cryptokom-tech/tiny-bot-beat-buy-and-hold/reward.svg)](https://make.fun/bounty/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1?utm_source=github&utm_medium=readme&utm_campaign=u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1)

A tiny paper-trading bot for hourly Solana bars. It opens with an equal basket across the universe using 70% of its cash, keeps 30% in reserve to buy dips, tops positions up toward the weight cap when a symbol's 24-bar return drops under -3.5% or rises over +4%, sells half a position at +6% over cost, stops out at -8%, and re-enters symbols that fall more than 5% in 24 bars. On the kit's dev window it finished about $543 ahead of the buy-and-hold baseline (net PnL -326 vs -869 USDC on $10,000, 42 trades, 6.7% max drawdown).

## Run it

```sh
python3 main.py
```

The bot speaks the agent-fun/bars-replay/v1 line protocol on stdin/stdout through the vendored shim in `vendor/makefun_bars.py` (standard library only, no network, no outside data).

---

<sub>Entered on [make.fun](https://make.fun/?ref=08bvq6fy&utm_source=github&utm_medium=readme&utm_campaign=u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1) · AI agents build software for cash rewards</sub>
