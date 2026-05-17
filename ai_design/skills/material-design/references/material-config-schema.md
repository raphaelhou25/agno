# 材料配置表结构与检索规则

## 概述

材料配置表是一个**静态文件数据源**（通常为 Excel / JSON / CSV 格式），由包装工程团队维护。本文件描述其字段结构、分区逻辑，以及智能体如何进行结构化检索。

> **实际部署时**：将真实配置表文件路径挂载到此目录，或通过 `GET /api/materials/config` 接口获取。智能体应优先读取实际文件；若文件不可访问，使用本文档作为 schema 参考并提示用户提供配置数据。

---

## 配置表分区

配置表分为三个分区（Sheet / 子表）：

| 分区 ID | 名称 | 用途 |
|--------|-----|-----|
| SHEET-A | 瓦楞纸板主材 | 箱体主体材料，含楞型、克重、ECT 等 |
| SHEET-B | 内衬缓冲材料 | EPE/EVA/蜂窝纸板/气柱袋等 |
| SHEET-C | 面纸与印刷材料 | 表面处理、印刷工艺（可选） |

---

## SHEET-A：瓦楞纸板主材

### 字段定义

| 字段名 | 类型 | 说明 |
|-------|-----|-----|
| `material_code` | string | 唯一材料编码，如 `BC-175-115` |
| `material_name` | string | 材料名称 |
| `flute_type` | enum | 楞型：E / B / C / A / BC / AB |
| `liner_weight_gsm` | number | 面纸克重（g/m²） |
| `medium_weight_gsm` | number | 芯纸克重（g/m²） |
| `board_thickness_mm` | number | 纸板厚度（mm） |
| `actual_ect_n_per_m` | number | 实测边压强度（N/m） |
| `actual_bct_base_n` | number | 标准箱型基准 BCT（N），400×300×300mm 规格 |
| `transport_modes` | array | 适用运输模式列表，如 `["land","sea","air"]` |
| `max_gross_weight_kg` | number | 建议最大使用毛重（kg） |
| `eco_level` | enum | 环保等级：standard / recyclable / biodegradable |
| `unit_price_rmb_m2` | number | 单价（元/m²） |
| `supplier_code` | string | 供应商编码 |
| `supply_stability_score` | number | 供应稳定性评分（0~10） |
| `stock_status` | enum | 库存状态：available / limited / on_order |
| `notes` | string | 备注（如认证、特殊工艺） |

### 示例数据

```json
[
  {
    "material_code": "BC-175-115",
    "material_name": "BC 双瓦楞（面纸175g 芯纸115g）",
    "flute_type": "BC",
    "liner_weight_gsm": 175,
    "medium_weight_gsm": 115,
    "board_thickness_mm": 7.0,
    "actual_ect_n_per_m": 9200,
    "actual_bct_base_n": 4200,
    "transport_modes": ["land", "sea", "air", "multimodal"],
    "max_gross_weight_kg": 30,
    "eco_level": "recyclable",
    "unit_price_rmb_m2": 12.5,
    "supplier_code": "SUP-001",
    "supply_stability_score": 9.2,
    "stock_status": "available",
    "notes": "通过 ISO 9001 认证"
  },
  {
    "material_code": "C-150-115",
    "material_name": "C 单瓦楞（面纸150g 芯纸115g）",
    "flute_type": "C",
    "liner_weight_gsm": 150,
    "medium_weight_gsm": 115,
    "board_thickness_mm": 3.6,
    "actual_ect_n_per_m": 6800,
    "actual_bct_base_n": 2800,
    "transport_modes": ["land", "sea"],
    "max_gross_weight_kg": 15,
    "eco_level": "recyclable",
    "unit_price_rmb_m2": 8.2,
    "supplier_code": "SUP-002",
    "supply_stability_score": 8.5,
    "stock_status": "available",
    "notes": ""
  }
]
```

---

## SHEET-B：内衬缓冲材料

### 字段定义

| 字段名 | 类型 | 说明 |
|-------|-----|-----|
| `material_code` | string | 唯一编码，如 `EPE-20` |
| `material_name` | string | 材料名称 |
| `cushion_type` | enum | 类型：EPE / EVA / honeycomb / air_column / polyurethane |
| `thickness_mm` | number | 标准厚度（mm） |
| `density_kg_m3` | number | 密度（kg/m³） |
| `max_weight_kg` | number | 适用最大产品重量（kg） |
| `applicable_fragility` | array | 适用易碎等级列表，如 `["medium","high"]` |
| `g_factor_support` | number | 可支持的最低 G 值（越低越保护） |
| `eco_level` | enum | 环保等级 |
| `unit_price_rmb_sheet` | number | 单价（元/张，标准 1m×1m） |
| `supplier_code` | string | 供应商编码 |
| `supply_stability_score` | number | 供应稳定性评分 |
| `stock_status` | enum | 库存状态 |

### 示例数据

```json
[
  {
    "material_code": "EPE-20",
    "material_name": "EPE 珍珠棉 20mm",
    "cushion_type": "EPE",
    "thickness_mm": 20,
    "density_kg_m3": 18,
    "max_weight_kg": 25,
    "applicable_fragility": ["medium", "high"],
    "g_factor_support": 25,
    "eco_level": "recyclable",
    "unit_price_rmb_sheet": 8.5,
    "supplier_code": "SUP-003",
    "supply_stability_score": 8.8,
    "stock_status": "available"
  },
  {
    "material_code": "EVA-15",
    "material_name": "EVA 泡棉 15mm",
    "cushion_type": "EVA",
    "thickness_mm": 15,
    "density_kg_m3": 45,
    "max_weight_kg": 10,
    "applicable_fragility": ["high", "very_high"],
    "g_factor_support": 15,
    "eco_level": "standard",
    "unit_price_rmb_sheet": 18.0,
    "supplier_code": "SUP-004",
    "supply_stability_score": 7.5,
    "stock_status": "available"
  }
]
```

---

## 检索执行规则

### 规则 1：硬约束过滤（必须全部满足）

```
主材检索硬约束：
  [H-A1] actual_ect_n_per_m >= target_ect_n_per_m（修正后目标 ECT）
  [H-A2] transport_mode IN material.transport_modes
  [H-A3] max_gross_weight_kg >= gross_weight_kg
  [H-A4] stock_status IN ["available", "limited"]
  [H-A5] eco_level 满足申请单 eco_requirement
         （none → 所有等级均可；recyclable → 排除 standard；biodegradable → 仅 biodegradable）

缓冲材检索硬约束：
  [H-B1] thickness_mm >= cushion_thickness_mm（计算所得最小厚度，已向上取整）
  [H-B2] fragility_level IN material.applicable_fragility
  [H-B3] max_weight_kg >= content_weight_kg
  [H-B4] g_factor_support <= G_required（支持的 G 值要低于或等于需求 G 值）
  [H-B5] stock_status IN ["available", "limited"]
```

### 规则 2：软约束过滤（理想满足，可分步放宽）

```
第一轮过滤：同时满足软约束
  [S-A1] unit_price_rmb_m2 × 用量 ≤ budget_rmb_per_unit × 0.60

若无结果，第二轮放宽：
  [S-A1'] unit_price_rmb_m2 × 用量 ≤ budget_rmb_per_unit × 0.75

若仍无结果，移除价格约束，仅保留硬约束，并在 unresolved_items 中标注超预算
```

### 规则 3：用量计算（主材）

主材用量（m²）按展开面积计算（RSC 箱型）：

```
单箱用量（m²）= 
  2 × [(L + W) × H + (L + W) × overlap_factor] / 1,000,000

其中：
  L = outer_length_mm
  W = outer_width_mm
  H = outer_height_mm
  overlap_factor = 0.05（5% 搭接余量）

单价（元/件）= 单箱用量(m²) × unit_price_rmb_m2
```

### 规则 4：无匹配结果处理

```
若主材检索无结果：
  Step 1：放宽价格约束（见规则 2）
  Step 2：若仍无结果，按 ECT 从高到低取最接近的 3 条，
          在 unresolved_items 标注 "ECT不满足" 及差距百分比
  Step 3：告知用户，提供最接近方案，请求用户决策（更换规格/接受偏差/人工介入）
```

### 规则 5：stock_status = "limited" 处理

```
当主选材料 stock_status = "limited"：
  - 正常参与选型
  - 在 result.warnings 中追加：{ "type": "stock_limited", "material_code": "...", "message": "该材料库存有限，建议尽快确认采购计划" }
```

---

## 配置表版本管理

配置表应包含以下元数据字段（在文件头部或独立 META 分区）：

```json
{
  "config_version": "2024.Q4.01",
  "last_updated": "2024-12-01",
  "updated_by": "张工",
  "valid_until": "2025-03-31",
  "notes": "新增 BC-200-115 超重型规格"
}
```

若配置表版本 `valid_until` 已过期，在结果 `warnings` 中追加提示，但不阻断流程。
