#!/usr/bin/env python3
"""
box_matcher.py — 箱体匹配引擎
用法: python scripts/box_matcher.py --input '<JSON字符串>'
输出: JSON格式的匹配结果，直接可被协调智能体消费

输入 JSON 示例:
{
  "product_dimensions": {"length_mm": 180, "width_mm": 80, "height_mm": 60},
  "product_weight_kg": 0.35,
  "quantity_per_box": 6,
  "transport_mode": "multimodal",
  "fragility_level": "high",
  "storage_conditions": "normal",
  "special_requirements": ""
}
"""

import argparse
import json
import sys
from itertools import permutations
from pathlib import Path

# ──────────────────────────────────────────────
# 1. 配置与常量
# ──────────────────────────────────────────────

MARGIN_TABLE = {
    "low":        {"air": 8,  "land": 10, "sea": 12, "multimodal": 12},
    "medium":     {"air": 12, "land": 15, "sea": 18, "multimodal": 18},
    "high":       {"air": 18, "land": 20, "sea": 25, "multimodal": 25},
    "ultra_high": {"air": 25, "land": 28, "sea": 32, "multimodal": 32},
}

OPERATION_MARGIN = 10  # 组装操作余量 mm（每方向两端共加 10mm）

CATALOG_FILE = Path(__file__).parent.parent / "references" / "box-catalog.md"


# ──────────────────────────────────────────────
# 2. 配置表解析
# ──────────────────────────────────────────────

def parse_catalog(filepath: Path) -> list:
    """从 Markdown 表格解析箱型数据"""
    boxes = []
    if not filepath.exists():
        return boxes

    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not (line.startswith("|") and "|" in line[1:]):
                continue
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) < 14:
                continue
            # 跳过表头行和分隔线
            if not cells[0] or cells[0].startswith("-") or cells[0] == "box_id":
                continue
            # 第3列（flute）应为字母，数字列应可转换
            try:
                int(cells[3])  # inner_L 必须是数字
            except ValueError:
                continue
            try:
                box = {
                    "box_id":           cells[0],
                    "box_type":         cells[1],
                    "flute_type":       cells[2],
                    "inner_L":          int(cells[3]),
                    "inner_W":          int(cells[4]),
                    "inner_H":          int(cells[5]),
                    "outer_L":          int(cells[6]),
                    "outer_W":          int(cells[7]),
                    "outer_H":          int(cells[8]),
                    "max_weight_kg":    float(cells[9]),
                    "bcl_n":            int(cells[10]),
                    "suitable_transport": [t.strip() for t in cells[11].split(",")],
                    "approx_cost_cny":  float(cells[12]),
                    "notes":            cells[13] if len(cells) > 13 else "",
                }
                boxes.append(box)
            except (ValueError, IndexError):
                continue

    return boxes


# ──────────────────────────────────────────────
# 3. 排列计算
# ──────────────────────────────────────────────

def get_factorizations(n: int) -> list:
    """返回 n 的所有有序三元因数分解 (nx, ny, nz)"""
    result = []
    for nx in range(1, n + 1):
        if n % nx != 0:
            continue
        rem = n // nx
        for ny in range(1, rem + 1):
            if rem % ny != 0:
                continue
            nz = rem // ny
            result.append((nx, ny, nz))
    return result


def find_best_arrangement(pL, pW, pH, quantity, margin):
    """枚举所有因数分解 × 6方向，返回体积最小的排列"""
    factorizations = get_factorizations(quantity)
    dim_perms = list(set(permutations([pL, pW, pH])))
    candidates = []

    for (nx, ny, nz) in factorizations:
        for (dx, dy, dz) in dim_perms:
            RL = nx * dx + 2 * margin + OPERATION_MARGIN
            RW = ny * dy + 2 * margin + OPERATION_MARGIN
            RH = nz * dz + 2 * margin + OPERATION_MARGIN
            volume = RL * RW * RH
            candidates.append({
                "nx": nx, "ny": ny, "nz": nz,
                "dim_x": dx, "dim_y": dy, "dim_z": dz,
                "required_L": round(RL, 1),
                "required_W": round(RW, 1),
                "required_H": round(RH, 1),
                "volume_mm3": volume,
            })

    if not candidates:
        return {}

    # 排序：体积优先，其次高度最矮
    candidates.sort(key=lambda c: (c["volume_mm3"], c["required_H"]))
    best = candidates[0]
    best["all_candidates_count"] = len(candidates)
    best["arrangement_label"] = (
        f"{best['nx']}x{best['ny']}x{best['nz']}"
        f"（{best['dim_x']}x{best['dim_y']}x{best['dim_z']}mm 沿 X/Y/Z）"
    )
    return best


# ──────────────────────────────────────────────
# 4. 筛选与评分
# ──────────────────────────────────────────────

def dims_fit(req, box_inner):
    """排序后逐维比较（允许旋转）"""
    return all(r <= b for r, b in zip(sorted(req, reverse=True),
                                       sorted(box_inner, reverse=True)))


def filter_candidates(boxes, req_dims, total_weight, transport_mode, relax=0):
    RL, RW, RH = req_dims
    if relax >= 1:
        RL = max(RL - OPERATION_MARGIN, 1)
        RW = max(RW - OPERATION_MARGIN, 1)
        RH = max(RH - OPERATION_MARGIN, 1)
    weight_factor = 0.9 if relax >= 2 else 1.0
    req = (RL, RW, RH)
    result = []
    for box in boxes:
        inner = (box["inner_L"], box["inner_W"], box["inner_H"])
        if not dims_fit(req, inner):
            continue
        if box["max_weight_kg"] < total_weight * weight_factor:
            continue
        result.append(box)
    return result


def score_box(box, req_dims, total_weight, transport_mode, min_cost, max_cost):
    inner_vol = box["inner_L"] * box["inner_W"] * box["inner_H"]
    req_vol = req_dims[0] * req_dims[1] * req_dims[2]
    space_ratio = req_vol / inner_vol if inner_vol > 0 else 0

    if 0.60 <= space_ratio <= 0.80:
        s_space = 1.0
    elif space_ratio < 0.60:
        s_space = space_ratio / 0.60
    else:
        s_space = max(0.0, (1.0 - space_ratio) / 0.20)

    w_ratio = total_weight / box["max_weight_kg"] if box["max_weight_kg"] > 0 else 0
    if 0.60 <= w_ratio <= 0.85:
        s_weight = 1.0
    elif w_ratio < 0.60:
        s_weight = w_ratio / 0.60
    else:
        s_weight = max(0.0, 1.0 - (w_ratio - 0.85) / 0.15)

    suitable = box["suitable_transport"]
    if transport_mode in suitable or "all" in suitable:
        s_transport = 1.0
    elif "multimodal" in suitable:
        s_transport = 0.85
    else:
        s_transport = 0.5

    cost_range = max_cost - min_cost
    s_cost = (max_cost - box["approx_cost_cny"]) / cost_range if cost_range > 0.01 else 1.0

    total = 0.40 * s_space + 0.30 * s_weight + 0.20 * s_transport + 0.10 * s_cost
    return {
        "score":               round(total, 4),
        "space_utilization_pct": round(space_ratio * 100, 1),
        "weight_utilization_pct": round(w_ratio * 100, 1),
        "score_space":         round(s_space, 4),
        "score_weight":        round(s_weight, 4),
        "score_transport":     round(s_transport, 4),
        "score_cost":          round(s_cost, 4),
    }


# ──────────────────────────────────────────────
# 5. 主流程
# ──────────────────────────────────────────────

def run_matching(inp: dict) -> dict:
    dims   = inp["product_dimensions"]
    pL     = float(dims["length_mm"])
    pW     = float(dims["width_mm"])
    pH     = float(dims["height_mm"])
    wt     = float(inp["product_weight_kg"])
    qty    = int(inp["quantity_per_box"])
    mode   = inp.get("transport_mode", "multimodal")
    frag   = inp.get("fragility_level", "medium")
    stor   = inp.get("storage_conditions", "normal")
    special = inp.get("special_requirements", "") or ""

    # 边距
    margin = MARGIN_TABLE.get(frag, MARGIN_TABLE["medium"]).get(
        mode, MARGIN_TABLE["medium"]["multimodal"]
    )
    if stor == "humid":
        margin += 3
    if any(kw in special.lower() for kw in ["锂电", "lithium", "li-ion"]):
        margin += 5

    total_weight = wt * qty + 0.5

    # 最优排列
    arr = find_best_arrangement(pL, pW, pH, qty, margin)
    if not arr:
        return {"status": "failed", "error_code": "CALC_ERROR",
                "error_message": "无法计算有效排列方案（quantity可能为0）"}

    req = (arr["required_L"], arr["required_W"], arr["required_H"])

    # 加载配置表
    boxes = parse_catalog(CATALOG_FILE)
    if not boxes:
        return {"status": "failed", "error_code": "CATALOG_NOT_FOUND",
                "error_message": str(CATALOG_FILE)}

    # 逐级放宽筛选
    candidates, relax_used = [], 0
    for lvl in range(3):
        candidates = filter_candidates(boxes, req, total_weight, mode, lvl)
        if candidates:
            relax_used = lvl
            break

    if not candidates:
        return {
            "status": "failed",
            "error_code": "NO_MATCH",
            "error_message": f"在 {len(boxes)} 种箱型中未找到满足约束的箱型",
            "debug_info": {
                "required_inner_mm": {"L": req[0], "W": req[1], "H": req[2]},
                "total_weight_kg": round(total_weight, 2),
            },
            "suggested_action": "建议减少单箱数量，或联系设计团队定制大承重箱型",
        }

    # 评分
    costs = [b["approx_cost_cny"] for b in candidates]
    scored = sorted(
        [(b, score_box(b, req, total_weight, mode, min(costs), max(costs)))
         for b in candidates],
        key=lambda x: x[1]["score"],
        reverse=True,
    )

    best_box, best_sc = scored[0]

    def fmt_box(box, sc, is_alt=False):
        d = {
            "box_id":       box["box_id"],
            "box_type":     box["box_type"],
            "flute_type":   box["flute_type"],
            "inner_dimensions":  {"length_mm": box["inner_L"], "width_mm": box["inner_W"], "height_mm": box["inner_H"]},
            "outer_dimensions":  {"length_mm": box["outer_L"], "width_mm": box["outer_W"], "height_mm": box["outer_H"]},
            "max_weight_capacity_kg": box["max_weight_kg"],
            "bcl_n":        box["bcl_n"],
            "suitable_transport": box["suitable_transport"],
            "approx_cost_cny":   box["approx_cost_cny"],
        }
        if not is_alt:
            d["arrangement"] = arr["arrangement_label"]
            d["configuration_notes"] = (
                f"内尺寸余量 L+{box['inner_L']-arr['required_L']:.0f}mm "
                f"W+{box['inner_W']-arr['required_W']:.0f}mm "
                f"H+{box['inner_H']-arr['required_H']:.0f}mm"
            )
        else:
            d["match_score"] = sc["score"]
            d["trade_off"] = (f"空间利用率{sc['space_utilization_pct']}%，"
                              f"承重利用率{sc['weight_utilization_pct']}%，"
                              f"成本{box['approx_cost_cny']}元/套")
        return d

    alts = [fmt_box(b, s, is_alt=True) for b, s in scored[1:3]]

    rationale = (
        f"产品 {pL:.0f}x{pW:.0f}x{pH:.0f}mm，{wt}kg，qty={qty}。"
        f"最优排列 {arr['arrangement_label']}，"
        f"最小需求内尺寸 {arr['required_L']:.0f}x{arr['required_W']:.0f}x{arr['required_H']:.0f}mm"
        f"（margin={margin}mm）。"
        f"{best_box['box_id']} 空间利用率{best_sc['space_utilization_pct']}%，"
        f"承重利用率{best_sc['weight_utilization_pct']}%，"
        f"综合评分{best_sc['score']}，为候选集最优。"
    )

    result = {
        "status": "success",
        "recommended_box": fmt_box(best_box, best_sc),
        "alternatives": alts,
        "match_score": best_sc["score"],
        "arrangement_detail": {
            "nx": arr["nx"], "ny": arr["ny"], "nz": arr["nz"],
            "product_orientation": f"{arr['dim_x']}x{arr['dim_y']}x{arr['dim_z']}mm",
            "min_required_inner_mm": {"length_mm": arr["required_L"],
                                       "width_mm":  arr["required_W"],
                                       "height_mm": arr["required_H"]},
            "margin_applied_mm": margin,
            "space_utilization_percent": best_sc["space_utilization_pct"],
            "total_arrangements_evaluated": arr.get("all_candidates_count", 0),
        },
        "selection_rationale": rationale,
        "catalog_version": "v2.1",
        "catalog_box_count": len(boxes),
        "relax_level_used": relax_used,
    }

    if relax_used > 0:
        result["warnings"] = [f"使用了降级匹配（level={relax_used}），建议人工复核"]

    return result


# ──────────────────────────────────────────────
# 6. 入口
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="request_form JSON字符串")
    args = parser.parse_args()
    try:
        inp = json.loads(args.input)
    except json.JSONDecodeError as e:
        print(json.dumps({"status": "failed", "error_code": "INVALID_INPUT",
                          "error_message": str(e)}, ensure_ascii=False, indent=2))
        sys.exit(1)
    print(json.dumps(run_matching(inp), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
