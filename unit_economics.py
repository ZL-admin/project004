#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
二次元 AI 角色扮演 App —— 单位经济（Unit Economics）测算
路线：纯 SFW + 双商店上架 + 现成 LLM API

用法：
    python3 unit_economics.py

说明：
    - MODELS 为 2026-05 各家公开报价（USD / 每百万 token）。
    - ASSUMPTIONS 为业务假设，请用你自己的真实日志校准后重跑。
    - 角色扮演成本几乎全在 input token（每条消息都要重发角色卡+历史+记忆），
      因此“模型档位”和“缓存命中率”是最大的两个杠杆。
"""

# ============ 1. LLM 定价（2026-05，USD / 百万 token）============
# in = 输入；out = 输出；cache_in = 缓存命中的输入价
# 多数厂商缓存命中 = 输入价的 10%；OpenAI 缓存命中 = 输入价的 50%。
MODELS = {
    "gemini-2.5-flash-lite": {"in": 0.10,  "out": 0.40,  "cache_in": 0.010},
    "gemini-2.5-flash":      {"in": 0.30,  "out": 2.50,  "cache_in": 0.030},
    "gemini-3.1-flash-lite": {"in": 0.25,  "out": 1.50,  "cache_in": 0.025},
    "gemini-3.5-flash":      {"in": 1.50,  "out": 9.00,  "cache_in": 0.150},
    "gpt-4o-mini":           {"in": 0.15,  "out": 0.60,  "cache_in": 0.075},
    "deepseek-v3":           {"in": 0.252, "out": 0.378, "cache_in": 0.0252},
}

# ============ 2. 业务假设（按需修改后重跑）============
ASSUMPTIONS = {
    # —— 单条消息的 token 结构（角色扮演典型值，强烈建议用真实日志校准）——
    "system_prompt_tokens": 800,    # 角色卡 + 系统指令
    "memory_tokens":        500,    # 长期记忆 / 摘要
    "history_tokens":       3000,   # 滑动窗口对话历史（稳态平均）
    "user_msg_tokens":      40,     # 用户单条输入
    "ai_reply_tokens":      220,    # AI 单条回复（roleplay 偏长）

    # —— 缓存 —— input 中可命中前缀缓存的比例（system+memory+稳定历史前缀）
    "cache_hit_ratio":      0.50,

    # —— 使用强度（条 / 月 / 人）——
    "free_msgs_per_month":  300,
    "paid_msgs_per_month":  1500,

    # —— 用户结构与变现 ——
    "paid_conversion":      0.03,   # 付费转化率
    "sub_price":            9.90,   # 订阅月价（标准档）
    "store_cut":            0.30,   # 应用商店抽成（首年 30%）
    "ad_arpu_free":         0.15,   # 每个免费用户每月广告收入
    "target_gross_margin":  0.60,   # 目标毛利率（用于反推付费用户 token 预算）
}

A = ASSUMPTIONS


# ============ 3. 计算 ============
def input_tokens():
    return (A["system_prompt_tokens"] + A["memory_tokens"]
            + A["history_tokens"] + A["user_msg_tokens"])


def msg_cost(model, cache_ratio=None):
    """单条消息成本（USD）。"""
    if cache_ratio is None:
        cache_ratio = A["cache_hit_ratio"]
    m = MODELS[model]
    inp = input_tokens()
    out = A["ai_reply_tokens"]
    cached = inp * cache_ratio
    uncached = inp * (1 - cache_ratio)
    return (uncached * m["in"] + cached * m["cache_in"] + out * m["out"]) / 1_000_000


def monthly_cost(model, msgs, cache_ratio=None):
    return msg_cost(model, cache_ratio) * msgs


def sub_net():
    """订阅扣除商店抽成后的净收入。"""
    return A["sub_price"] * (1 - A["store_cut"])


def pnl_per_n(model, n=1000, cache_ratio=None, with_ads=True):
    conv = A["paid_conversion"]
    paid_n = n * conv
    free_n = n - paid_n
    llm = (paid_n * monthly_cost(model, A["paid_msgs_per_month"], cache_ratio)
           + free_n * monthly_cost(model, A["free_msgs_per_month"], cache_ratio))
    rev = paid_n * sub_net() + (free_n * A["ad_arpu_free"] if with_ads else 0.0)
    return rev, llm, rev - llm


def breakeven_conversion(model, cache_ratio=None, with_ads=True):
    """打平 LLM 成本所需的付费转化率；返回 (状态, 值)。"""
    pc = monthly_cost(model, A["paid_msgs_per_month"], cache_ratio)
    fc = monthly_cost(model, A["free_msgs_per_month"], cache_ratio)
    ad = A["ad_arpu_free"] if with_ads else 0.0
    a_term = sub_net() - pc        # 每付费用户净贡献
    b_term = ad - fc               # 每免费用户净贡献
    if a_term <= 0:                # 付费用户本身就亏 -> 扩张必亏
        return ("infeasible", None)
    if b_term >= 0:                # 免费用户已被广告覆盖 -> 任意转化都盈利
        return ("profitable", 0.0)
    c = -b_term / (a_term - b_term)
    if c > 1:
        return ("infeasible", c)
    return ("ok", c)


def max_paid_msgs(model, cache_ratio=None):
    """付费用户在目标毛利下每月可发的最大消息数。"""
    budget = sub_net() * (1 - A["target_gross_margin"])
    return budget / msg_cost(model, cache_ratio)


# ============ 4. 打印 ============
def line(cols, widths, left_cols=(0,)):
    out = []
    for i, (c, w) in enumerate(zip(cols, widths)):
        s = str(c)
        out.append(s.ljust(w) if i in left_cols else s.rjust(w))
    return "".join(out)


def hr(ch="=", n=78):
    print(ch * n)


def main():
    hr()
    print("二次元 AI 角色扮演 App —— 单位经济测算 (定价基准 2026-05)")
    hr()

    # --- 假设回显 ---
    print("\n[假设] 单条消息 token 结构")
    print(f"  输入合计 input/msg : {input_tokens():,} tokens "
          f"(system {A['system_prompt_tokens']} + memory {A['memory_tokens']} "
          f"+ history {A['history_tokens']} + user {A['user_msg_tokens']})")
    print(f"  输出      output/msg: {A['ai_reply_tokens']:,} tokens")
    print(f"  缓存命中率 cache_hit : {A['cache_hit_ratio']*100:.0f}%")
    print(f"  使用强度  free/paid : {A['free_msgs_per_month']} / "
          f"{A['paid_msgs_per_month']} 条每月")
    print(f"  变现      转化/订阅 : {A['paid_conversion']*100:.1f}% / "
          f"${A['sub_price']}（商店抽成 {A['store_cut']*100:.0f}%，净 ${sub_net():.2f}）"
          f" + 免费广告 ${A['ad_arpu_free']}/人/月")

    # --- 表1：每条消息 & 每用户每月成本 ---
    print("\n[表1] 各模型成本（带缓存 / 不带缓存）")
    w = [24, 13, 13, 13, 13]
    print(line(["Model", "$/msg(cache)", "$/msg(raw)", "Free/mo", "Paid/mo"], w))
    hr("-")
    for name in MODELS:
        c_cache = msg_cost(name, A["cache_hit_ratio"])
        c_raw = msg_cost(name, 0.0)
        free_mo = monthly_cost(name, A["free_msgs_per_month"], A["cache_hit_ratio"])
        paid_mo = monthly_cost(name, A["paid_msgs_per_month"], A["cache_hit_ratio"])
        print(line([name, f"${c_cache:.5f}", f"${c_raw:.5f}",
                    f"${free_mo:.3f}", f"${paid_mo:.3f}"], w))

    # --- 表2：每 1000 MAU 的 P&L（带缓存）---
    print("\n[表2] 单位经济 P&L（每 1000 MAU / 月，含订阅+广告，带缓存）")
    w = [24, 12, 12, 12, 10]
    print(line(["Model", "Revenue", "LLM cost", "Gross", "Margin"], w))
    hr("-")
    for name in MODELS:
        rev, llm, gross = pnl_per_n(name, 1000)
        margin = (gross / rev * 100) if rev else 0
        print(line([name, f"${rev:,.0f}", f"${llm:,.0f}",
                    f"${gross:,.0f}", f"{margin:.0f}%"], w))

    # --- 表3：盈亏平衡转化率 & 付费 token 预算 ---
    print("\n[表3] 打平所需付费转化率 & 付费用户消息预算")
    w = [24, 16, 16, 18]
    print(line(["Model", "BE conv(+ads)", "BE conv(no ad)", "MaxPaidMsgs@60%"], w))
    hr("-")

    def fmt_be(res):
        status, val = res
        if status == "profitable":
            return "已盈利(广告覆盖)"
        if status == "infeasible":
            return "不可行" + (f"({val*100:.0f}%)" if val else "")
        return f"{val*100:.2f}%"

    for name in MODELS:
        be_ads = breakeven_conversion(name, with_ads=True)
        be_noad = breakeven_conversion(name, with_ads=False)
        mpm = max_paid_msgs(name)
        print(line([name, fmt_be(be_ads), fmt_be(be_noad), f"{mpm:,.0f}"], w))

    # --- 表4：敏感性 —— Flash-Lite 不同使用强度 ---
    print("\n[表4] 敏感性：gemini-2.5-flash-lite 在不同月消息量下的每用户成本")
    w = [18, 18]
    print(line(["Msgs/month", "$/user/month"], w))
    hr("-")
    for msgs in (100, 300, 600, 1000, 2000, 4000):
        mc = monthly_cost("gemini-2.5-flash-lite", msgs, A["cache_hit_ratio"])
        print(line([f"{msgs:,}", f"${mc:.3f}"], w))

    print("\n要点：免费层务必用最便宜的模型（Flash-Lite 档）；高价模型只留给付费/重度用户。")
    print("     提高缓存命中率 = 直接降本，是工程上回报最高的一项优化。")
    hr()


if __name__ == "__main__":
    main()
