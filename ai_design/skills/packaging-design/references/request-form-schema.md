# 外包装设计申请单字段规范

本文档定义申请单中所有字段的类型、约束和说明，供协调智能体解析申请单时参考。

---

## 必填字段

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `product_name` | string | 非空，最长 100 字符 | 产品名称 |
| `product_dimensions.length_mm` | number | > 0，单位 mm | 产品长度（净尺寸，不含包装） |
| `product_dimensions.width_mm` | number | > 0，单位 mm | 产品宽度（净尺寸） |
| `product_dimensions.height_mm` | number | > 0，单位 mm | 产品高度（净尺寸） |
| `product_weight_kg` | number | > 0，单位 kg | 单件产品重量 |
| `quantity_per_box` | integer | ≥ 1 | 每箱装配数量 |
| `transport_mode` | enum | 见下方枚举值 | 运输方式 |

**transport_mode 枚举值**：
- `air`：空运
- `sea`：海运
- `land`：陆运
- `multimodal`：多式联运

---

## 可选字段（缺失时使用默认值）

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `drop_height_requirement` | string | 按运输方式自动推算 | 跌落高度要求，如 "1.2m" 或 "按标准" |
| `storage_conditions` | string | `"normal"` | 存储条件：`normal` / `cold_chain` / `humid` / `high_temp` |
| `stacking_layers` | integer | 5 | 预期仓储堆叠层数 |
| `target_cost_per_unit_cny` | number | null（不约束） | 每套包装目标成本（元人民币） |
| `fragility_level` | enum | `"medium"` | 产品易碎程度：`low` / `medium` / `high` / `ultra_high` |
| `special_requirements` | string | `""` | 自由文本，描述特殊要求（防潮、防震、防静电等） |
| `certifications_required` | array[string] | `[]` | 需要符合的认证标准，如 `["ISTA-2A", "ASTM-D4169"]` |
| `design_reference_id` | string | null | 参考历史方案编号（相似性分析优先检索该方案周边） |

---

## 字段解析优先级

申请单可能以多种形式提交：

1. **结构化 JSON/表单**：直接映射到上述字段
2. **自然语言描述**：协调智能体提取关键信息，无法提取的必填字段需向用户追问
3. **文档上传（PDF/Word）**：由协调智能体读取并提取结构化信息

提取到字段后，统一转换为 SI 单位（mm、kg）存储，忽略用户原始单位（cm/g/lb 等需换算）。

---

## 申请单示例（JSON 格式）

```json
{
  "product_name": "蓝牙耳机 Pro X",
  "product_dimensions": {
    "length_mm": 180,
    "width_mm": 80,
    "height_mm": 60
  },
  "product_weight_kg": 0.35,
  "quantity_per_box": 6,
  "transport_mode": "multimodal",
  "drop_height_requirement": "1.0m",
  "storage_conditions": "normal",
  "stacking_layers": 8,
  "target_cost_per_unit_cny": 12.0,
  "fragility_level": "high",
  "special_requirements": "需防静电，产品含锂电池，运输需符合UN38.3",
  "certifications_required": ["ISTA-2A"],
  "design_reference_id": null
}
```
