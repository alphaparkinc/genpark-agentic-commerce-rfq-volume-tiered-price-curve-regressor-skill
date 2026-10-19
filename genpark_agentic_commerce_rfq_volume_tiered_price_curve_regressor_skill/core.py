# -*- coding: utf-8 -*-
"""B2B RFQ Volume Tiered Price Curve Regressor Skill for GenPark Agentic Commerce."""
import json
import math
from typing import Dict, Any, List

def fit_volume_price_elasticity_curve(vendor_name: str, tiers: List[Dict[str, Any]]) -> Dict[str, Any]:
    if len(tiers) < 2:
        return {"error": "At least 2 volume tiers required for regression fitting"}

    # Sort tiers by quantity ascending
    sorted_tiers = sorted(tiers, key=lambda x: x["quantity"])
    
    # Calculate log-log points for P = a * Q^b => ln(P) = ln(a) + b * ln(Q)
    n = len(sorted_tiers)
    sum_x = 0.0
    sum_y = 0.0
    sum_xx = 0.0
    sum_xy = 0.0

    for t in sorted_tiers:
        q = float(t["quantity"])
        p = float(t["unit_price_usd"])
        if q <= 0 or p <= 0:
            continue
        ln_q = math.log(q)
        ln_p = math.log(p)
        sum_x += ln_q
        sum_y += ln_p
        sum_xx += ln_q * ln_q
        sum_xy += ln_q * ln_p

    denominator = (n * sum_xx - sum_x * sum_x)
    if abs(denominator) < 1e-9:
        b = -0.15
        a = sorted_tiers[0]["unit_price_usd"]
    else:
        b = (n * sum_xy - sum_x * sum_y) / denominator
        ln_a = (sum_y - b * sum_x) / n
        a = math.exp(ln_a)

    # Elasticity index
    discount_competitiveness = "AGGRESSIVE_SCALE" if b < -0.20 else ("MODERATE_FAIR" if b < -0.08 else "FLAT_LOW_DISCOUNT")

    predictions = []
    for q_target in [sorted_tiers[0]["quantity"] * 2, sorted_tiers[-1]["quantity"] * 2]:
        pred_p = round(a * (q_target ** b), 2)
        predictions.append({"target_quantity": q_target, "model_fair_unit_price_usd": pred_p})

    return {
        "vendor": vendor_name,
        "fitted_power_law_model": f"Unit Price = {round(a, 2)} * Q^({round(b, 4)})",
        "elasticity_exponent_b": round(b, 4),
        "discount_competitiveness_tier": discount_competitiveness,
        "projected_extrapolations": predictions,
        "negotiation_leverage": "High volume leverage available; demand additional concession at next order breakpoint." if b > -0.10 else "Supplier offers robust structural manufacturing scale discounts.",
        "analyzer": "GenPark Industrial Procurement Arbiter"
    }

def identify_hidden_surcharge_break_points(tiers: List[Dict[str, Any]]) -> Dict[str, Any]:
    sorted_tiers = sorted(tiers, key=lambda x: x["quantity"])
    anomalies = []

    for i in range(len(sorted_tiers) - 1):
        q1 = sorted_tiers[i]["quantity"]
        p1 = sorted_tiers[i]["unit_price_usd"]
        q2 = sorted_tiers[i + 1]["quantity"]
        p2 = sorted_tiers[i + 1]["unit_price_usd"]

        total_cost1 = q1 * p1
        total_cost2 = q2 * p2
        marginal_quantity = q2 - q1
        marginal_cost = total_cost2 - total_cost1
        marginal_unit_cost = round(marginal_cost / marginal_quantity, 2) if marginal_quantity > 0 else 0.0

        # Marginal unit cost should never exceed previous base price
        if marginal_unit_cost > p1:
            anomalies.append({
                "tier_step": f"{q1} -> {q2} units",
                "base_price": p1,
                "apparent_discounted_price": p2,
                "effective_marginal_unit_cost": marginal_unit_cost,
                "infraction": "DISCOUNT_PARADOX: Marginal unit cost in step is higher than base price, indicating hidden setup fees or minimum order penalties."
            })

    return {
        "screened_tier_count": len(sorted_tiers),
        "anomalies_detected": anomalies,
        "has_pricing_irregularities": len(anomalies) > 0,
        "audit_verdict": "FLAGGED_FOR_AUDIT" if anomalies else "CLEAN_CONVEX_PRICING"
    }
