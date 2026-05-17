# 子智能体接口规范

本文档定义每个子智能体的调用契约（输入/输出格式），供协调智能体准确传递上下文和解析返回结果。

---

## 目录
- [box-design-agent（箱体设计）](#box-design-agent)
- [material-design-agent（材料设计）](#material-design-agent)
- [stacking-analysis-agent（堆叠分析）](#stacking-analysis-agent)
- [cost-analysis-agent（成本分析）](#cost-analysis-agent)
- [similarity-analysis-agent（相似性分析）](#similarity-analysis-agent)
- [plan-organization-agent（方案整理）](#plan-organization-agent)

---

## box-design-agent

**技能路径**：`box-design-agent/SKILL.md`

**触发方式**：协调智能体在 Step 1 直接传入申请单调用

### 输入（传给子智能体的 prompt 中包含）

```json
{
  "request_form": { /* 完整申请单，见 request-form-schema.md */ }
}
```

### 输出（子智能体返回，存入 DesignContext.results.box_design）

```json
{
  "recommended_box": {
    "box_id": "RSC-B-300x200x150",
    "box_type": "RSC",
    "inner_dimensions": { "length_mm": 300, "width_mm": 200, "height_mm": 150 },
    "outer_dimensions": { "length_mm": 310, "width_mm": 210, "height_mm": 158 },
    "flute_type": "B",
    "max_weight_capacity_kg": 15.0,
    "configuration_notes": "支持 2×3 排列，建议纵向竖放"
  },
  "alternatives": [
    {
      "box_id": "RSC-C-320x210x155",
      "match_score": 0.84,
      "trade_off": "外形稍大，成本约高 8%"
    }
  ],
  "match_score": 0.92,
  "selection_rationale": "产品净尺寸 180×80×60mm，6件排列后占用空间 280×170×140mm，RSC-B-300x200x150 提供 10mm 内衬余量，满足跌落防护需求。"
}
```

### 错误输出格式

```json
{
  "status": "failed",
  "error_code": "NO_MATCH",
  "error_message": "无法在配置表中找到满足尺寸约束的箱型",
  "suggested_action": "建议将产品尺寸容差放宽至 ±20mm 或减少单箱装配数量"
}
```

---

## material-design-agent

**技能路径**：`material-design-agent/SKILL.md`

### 输入

```json
{
  "request_form": { /* 完整申请单 */ },
  "box_design": { /* Step 1 完整结果 */ }
}
```

### 计算公式（子智能体内部使用，此处为协调者信息参考）

- **跌落高度推算**（当申请单未指定时）：
  - 空运：`H = 1.5m`
  - 海运：`H = 1.0m`
  - 陆运：`H = 0.8m`
  - 多式联运：`H = max(各运输方式)`
- **瓦楞纸抗压强度**：`BCT = K × ECT × √(Z × h)`（具体系数见子智能体 skill）
- **缓冲材料厚度**：`T = G × H / (σ_max × ε_opt)`

### 输出（存入 DesignContext.results.material_design）

```json
{
  "outer_box_material": {
    "material_id": "CORR-B-200",
    "description": "B 瓦楞双面牛皮纸",
    "ect_n_per_m": 5800,
    "bcl_n": 2400,
    "thickness_mm": 3.0
  },
  "cushioning_material": {
    "material_id": "EPE-25",
    "description": "EPE 珍珠棉，密度 25kg/m³",
    "thickness_mm": 20,
    "placement": "六面围护"
  },
  "calculated_drop_height_m": 1.2,
  "compression_strength_n": 2400,
  "design_parameters": {
    "fragility_g_value": 40,
    "cushion_efficiency": 0.45,
    "safety_factor": 1.5
  },
  "selection_rationale": "...",
  "requires_manual_review": false,
  "manual_review_notes": ""
}
```

---

## stacking-analysis-agent

**技能路径**：`stacking-analysis-agent/SKILL.md`

### 输入

```json
{
  "request_form": { /* 完整申请单 */ },
  "box_design": { /* Step 1 结果 */ },
  "material_design": { /* Step 2 结果 */ }
}
```

### API 调用（子智能体职责，协调者不直接调用）

子智能体调用堆叠计算 API（端点配置见子智能体 skill 中的 `config.md`），协调者无需关心 API 细节。

### 输出（存入 DesignContext.results.analysis.stacking）

```json
{
  "status": "success",
  "max_stacking_layers": 10,
  "recommended_stacking_layers": 8,
  "static_load_limit_kg": 320.0,
  "safety_margin_percent": 35.0,
  "stability_score": 0.88,
  "failure_mode": "压溃（底部第9层）",
  "recommendations": "建议使用托盘码放，超过8层时加铺隔板"
}
```

### 错误输出格式

```json
{
  "status": "failed",
  "error_code": "API_TIMEOUT",
  "error_message": "堆叠计算 API 超时",
  "retry_attempted": true
}
```

---

## cost-analysis-agent

**技能路径**：`cost-analysis-agent/SKILL.md`

### 输入

```json
{
  "request_form": { /* 完整申请单 */ },
  "box_design": { /* Step 1 结果 */ },
  "material_design": { /* Step 2 结果 */ }
}
```

### 成本公式（子智能体内部使用）

- **纸箱成本** = 展开面积(m²) × 材料单价(元/m²) + 加工费
- **缓冲材料成本** = 用量(m³) × 单价(元/m³)
- **附材成本**（胶带/标签等）= 固定加成系数 × (纸箱+缓冲)
- **单套总成本** = 纸箱 + 缓冲 + 附材

### 输出（存入 DesignContext.results.analysis.cost）

```json
{
  "status": "success",
  "cost_breakdown": {
    "outer_box_cny": 3.20,
    "cushioning_cny": 2.80,
    "accessories_cny": 0.45,
    "total_per_unit_cny": 6.45
  },
  "annual_volume_estimate": null,
  "meets_target_cost": true,
  "cost_vs_target_percent": -46.3,
  "optimization_suggestions": "可将 EPE 厚度由 20mm 降至 15mm，节省约 0.6 元/套，需重新验证跌落防护"
}
```

---

## similarity-analysis-agent

**技能路径**：`similarity-analysis-agent/SKILL.md`

### 输入

```json
{
  "request_form": { /* 完整申请单 */ },
  "box_design": { /* Step 1 结果 */ },
  "material_design": { /* Step 2 结果 */ },
  "design_reference_id": null
}
```

### 检索逻辑（子智能体职责）

从历史设计数据库中，依据以下维度向量检索相似方案：
- 产品尺寸比例
- 重量区间
- 运输方式
- 材料类型组合

返回 Top-3 最相似历史案例。

### 输出（存入 DesignContext.results.analysis.similarity）

```json
{
  "status": "success",
  "similar_cases": [
    {
      "design_id": "PKG-20231105-012",
      "product_name": "TWS 耳机旗舰款",
      "similarity_score": 0.91,
      "key_similarities": ["尺寸相近", "B瓦楞+EPE组合", "多式联运"],
      "outcome": "通过 ISTA-2A 认证，量产成本 6.8 元/套",
      "lessons_learned": "内衬分隔件建议改用纸浆模塑，耐湿性更好"
    }
  ],
  "recommendation": "当前方案与历史案例 PKG-20231105-012 高度相似，建议参考其认证流程"
}
```

---

## plan-organization-agent

**技能路径**：`plan-organization-agent/SKILL.md`

### 输入

```json
{
  "design_context": { /* 完整 DesignContext，含所有步骤结果 */ }
}
```

### 输出格式

参见 `references/output-format.md`，子智能体按该模板生成最终方案 Markdown 文档。

输出存入 `DesignContext.results.final_plan`，并直接呈现给用户。
