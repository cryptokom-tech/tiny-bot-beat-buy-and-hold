"""Tiny paper-trading bot for agent-fun/bars-replay/v1 (make.fun bounty
u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1).

The bot speaks the bars-replay line protocol through the vendored shim:
the harness sends a hello, then one batch of hourly bars at a time, and
the bot answers each batch with orders. Orders decided on a batch fill
at the next bar's open.

Strategy (long only, no leverage, deterministic):
  * On the first tradable batch, buy an equal slice of every priced
    symbol, spending 70% of the cash (each slice capped by the weight
    cap). Keeping 30% in reserve funds the dip buys below.
  * Every batch, for each held symbol:
      - stop-loss: sell everything when the position is worth 8% or
        more under its cost;
      - take profit: sell half when it is worth 6% or more over cost;
      - top up toward the weight cap when the 24-bar return is under
        -3.5% (buy the dip) or over +4% (add to a winner).
  * For a symbol not held: buy toward the weight cap when its 24-bar
    return is under -5% (a deep dip worth re-entering).
  * Trade pacing: the guardrails ask for at least 8 filled trades, so
    from batch 40 on, while fewer than 8 trades have filled, place one
    small trade in the strongest 12-bar symbol.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

MAX_SLIPPAGE_BPS = 10_000
INIT_PCT = 70          # percent of cash spent on the opening basket
DIP_BPS = -350         # 24-bar return under this tops a position up
TREND_BPS = 400        # 24-bar return over this tops a position up
REENTER_BPS = -500     # 24-bar return under this re-enters a symbol
STOP_PCT = 92          # sell all at or under 92% of cost
TAKE_PCT = 106         # sell half at or over 106% of cost
PACE_FROM = 40         # batch to start trade pacing
PACE_MIN_TRADES = 8
PACE_USDC = 150

closes = {}            # symbol -> list of closes (ints at price_scale)
started = False
trades_filled = 0


def ret_bps(symbol, bars_back):
    """Return over the last `bars_back` bars of `symbol`, in bps, or None."""
    series = closes.get(symbol, [])
    if len(series) <= bars_back or series[-1 - bars_back] == 0:
        return None
    return series[-1] * 10_000 // series[-1 - bars_back] - 10_000


def buy(symbol, amount):
    return {"side": "buy", "symbol": symbol,
            "notional_quote_units": amount, "max_slippage_bps": MAX_SLIPPAGE_BPS}


def sell(symbol, qty):
    return {"side": "sell", "symbol": symbol,
            "qty": qty, "max_slippage_bps": MAX_SLIPPAGE_BPS}


def on_batch(state, batch):
    global started, trades_filled
    for bar in batch["bars"]:
        closes.setdefault(bar["symbol"], []).append(int(bar["c"]))
    for fill in batch.get("fills", []):
        if fill.get("status") == "filled" and not str(fill.get("client_id", "")).startswith("_"):
            trades_filled += 1
    if state.warming_up:
        return []

    hello = state.hello
    caps = hello["caps"]
    min_notional = int(hello["fees"]["min_notional_quote_units"])
    symbols = [s["symbol"] for s in hello["symbols"]]

    if not started:
        priced = [s for s in symbols if state.close(s) is not None]
        if not priced:
            return []
        started = True
        n = min(len(priced), caps["max_open_positions"], caps["max_orders_per_bar"])
        by_weight = caps["max_weight_bps"] * state.equity // 10_000
        slice_ = min(state.cash * INIT_PCT // 100 // n, by_weight)
        if slice_ < min_notional:
            return []
        return [buy(s, slice_) for s in priced[:n]]

    orders = []
    cash = state.cash
    dust = state.equity * 2 // 100  # ignore top-ups worth 2% of equity or less
    for symbol in symbols:
        held = state.positions.get(symbol)
        r24 = ret_bps(symbol, 24)
        if held is not None:
            value = state.value(symbol, held.qty)
            if held.cost > 0 and value * 100 <= held.cost * STOP_PCT:
                orders.append(sell(symbol, held.qty))
                continue
            if held.cost > 0 and value * 100 >= held.cost * TAKE_PCT and held.qty > 1:
                orders.append(sell(symbol, held.qty // 2))
                continue
            if r24 is not None and (r24 < DIP_BPS or r24 > TREND_BPS):
                room = state.weight_room(symbol)
                if room > dust and cash >= min_notional:
                    spend = min(room, cash)
                    orders.append(buy(symbol, spend))
                    cash -= spend
        else:
            if r24 is not None and r24 < REENTER_BPS and cash >= min_notional:
                spend = min(state.weight_room(symbol), cash)
                if spend >= min_notional:
                    orders.append(buy(symbol, spend))
                    cash -= spend

    if not orders and state.seq >= PACE_FROM and trades_filled < PACE_MIN_TRADES:
        scale = 10 ** hello["capital"]["quote_scale"]
        candidates = [s for s in symbols if ret_bps(s, 12) is not None]
        if candidates:
            best = max(candidates, key=lambda s: (ret_bps(s, 12), s))
            held = state.positions.get(best)
            if held is not None:
                orders.append(sell(best, held.qty))
            elif cash >= PACE_USDC * scale:
                orders.append(buy(best, PACE_USDC * scale))

    return orders[: caps["max_orders_per_bar"]]


makefun_bars.run(on_batch)
