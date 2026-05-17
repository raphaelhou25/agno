# 材料力学参数计算公式参考

## 目录

- [F-01 跌落高度](#f-01-跌落高度)
- [F-02 目标 BCT（箱体抗压强度）](#f-02-目标-bct)
- [F-03 目标 ECT（边压强度）— McKee 公式](#f-03-目标-ect--mckee-公式)
- [F-04 缓冲厚度](#f-04-缓冲厚度)
- [F-05 湿度修正系数](#f-05-湿度修正系数)
- [F-06 纸板厚度与 ECT 换算](#f-06-纸板厚度与-ect-换算)
- [附录 A 参数查找表](#附录-a-参数查找表)

---

## F-01 跌落高度

**公式 ID**：F-01  
**用途**：根据产品毛重和运输模式，确定包装设计所需承受的跌落高度。

### 主公式（ISTA 2A / ASTM D5276 参考）

```
drop_height_mm = base_height_mm × transport_mode_factor
```

### 参数说明

**base_height_mm**：根据毛重查表

| 毛重范围（kg） | base_height_mm |
|------------|--------------|
| ≤ 4.5      | 900          |
| 4.6 ~ 9.0  | 760          |
| 9.1 ~ 18.0 | 610          |
| 18.1 ~ 27.0| 460          |
| 27.1 ~ 45.0| 380          |
| > 45.0     | 300          |

**transport_mode_factor**：

| 运输模式      | 系数  |
|------------|------|
| air（航空）   | 1.20 |
| multimodal  | 1.10 |
| land（陆运）  | 1.00 |
| sea（海运）   | 0.90 |

### 计算示例

```
输入：gross_weight_kg = 12, transport_mode = "land"
base_height_mm = 610（查表）
transport_mode_factor = 1.00
drop_height_mm = 610 × 1.00 = 610mm
```

---

## F-02 目标 BCT

**公式 ID**：F-02  
**用途**：计算箱体在存储和运输条件下所需的最小抗压强度（Box Compression Test）。

### 主公式

```
target_bct_n = gross_weight_kg × 9.8 × (stacking_layers - 1) × safety_factor
```

### 参数说明

**safety_factor**：综合安全系数，根据运输模式和 drop_height_mm 确定

| 运输模式 | drop_height_mm | safety_factor |
|--------|--------------|--------------|
| sea    | ≤ 600        | 3.5          |
| sea    | > 600        | 4.0          |
| land   | ≤ 600        | 4.0          |
| land   | > 600        | 4.5          |
| air    | any          | 5.0          |
| multimodal | any     | 4.5          |

> ⚠️ 当 stacking_layers = 1 时，safety_factor 取 1.5（单层最小静压要求）

### 计算示例

```
输入：gross_weight_kg = 12, stacking_layers = 5, transport_mode = "land", drop_height_mm = 610
safety_factor = 4.5（land + drop > 600）
target_bct_n = 12 × 9.8 × (5 - 1) × 4.5 = 12 × 9.8 × 4 × 4.5 = 2,116.8 ≈ 2,117N
```

---

## F-03 目标 ECT — McKee 公式

**公式 ID**：F-03  
**用途**：由目标 BCT 反推瓦楞纸板所需的最小边压强度（Edge Crush Test）。

### McKee 公式（简化版，适用于 RSC 箱型）

```
BCT = 5.87 × ECT × √(Z × t)

=> ECT = BCT / (5.87 × √(Z × t))
```

其中：
- `BCT`：目标 BCT（N），此处使用 `adjusted_bct_n`（湿度修正后）
- `ECT`：边压强度（N/m），即所求量
- `Z`：箱体周长（m）= `(inner_length_mm + inner_width_mm) × 2 / 1000`
- `t`：纸板厚度（m），初始估算时按楞型选取（见附录 A）

### 初始厚度估算（按楞型）

| 楞型 | 厚度 t (mm) | 典型应用 |
|-----|-----------|---------|
| E 楞 | 1.5       | 轻型、高印刷质量 |
| B 楞 | 2.5       | 内箱、中等强度 |
| C 楞 | 3.6       | 通用外箱 |
| A 楞 | 4.7       | 高垂直抗压 |
| BC 双楞 | 7.0    | 重型、高堆叠 |
| AB 双楞 | 8.0    | 超重型 |

> **选楞初始假设策略**：
> - gross_weight_kg ≤ 5：从 B 楞开始试算
> - 5 < gross_weight_kg ≤ 20：从 C 楞开始试算
> - gross_weight_kg > 20：从 BC 楞开始试算

### 计算示例

```
输入：adjusted_bct_n = 2,925, inner_L = 400mm, inner_W = 300mm, 假设 t = 3.6mm (C 楞)
Z = (400 + 300) × 2 / 1000 = 1.4m
t = 3.6 / 1000 = 0.0036m
ECT = 2,925 / (5.87 × √(1.4 × 0.0036))
    = 2,925 / (5.87 × √0.00504)
    = 2,925 / (5.87 × 0.07099)
    = 2,925 / 0.4167
    ≈ 7,018 N/m ≈ 7.0 kN/m
```

---

## F-04 缓冲厚度

**公式 ID**：F-04  
**用途**：根据跌落高度和内容物易碎程度，计算所需缓冲材料厚度。

### 主公式（基于 G 因子缓冲曲线方法）

```
cushion_thickness_mm = drop_height_mm × cushion_factor / G_required
```

其中：
- `drop_height_mm`：来自 F-01
- `G_required`：内容物允许的最大冲击加速度（G 值），根据 fragility_level 查表
- `cushion_factor`：缓冲材料系数，根据材料类型查表

### fragility_level → G_required 对照表

| fragility_level | G_required | 说明 |
|----------------|-----------|-----|
| low             | 无需缓冲（返回 0）| 普通硬质产品 |
| medium          | 40G       | 家电、工具 |
| high            | 25G       | 精密仪器、玻璃 |
| very_high       | 15G       | 光学元件、芯片 |

### cushion_factor（按材料类型）

| 缓冲材料     | cushion_factor | 适用场景 |
|-----------|--------------|---------|
| EPE 珍珠棉  | 0.15         | 通用，中等保护 |
| EVA 泡棉   | 0.12         | 高回弹，精密品 |
| 蜂窝纸板    | 0.18         | 环保，轻量 |
| 气柱袋     | 0.10         | 液体、异形品 |
| 聚氨酯泡沫  | 0.09         | 超精密，最高保护 |

> **缓冲材料预筛选逻辑**（在配置表检索前应用）：
> - fragility_level = medium：优先 EPE、蜂窝纸板
> - fragility_level = high：优先 EVA、EPE
> - fragility_level = very_high：优先聚氨酯、EVA；并在结果中标注需专业工程师复核

### 计算示例

```
输入：drop_height_mm = 610, fragility_level = "high", 预选材料 EPE
G_required = 25
cushion_factor = 0.15（EPE）
cushion_thickness_mm = 610 × 0.15 / 25 = 91.5 / 25 = 3.66mm

取整后向上取常规厚度规格（5mm 步进）= 5mm
```

> ⚠️ **取整规则**：计算值向上取最接近的标准厚度（5mm 步进，最小 10mm，最大 50mm）。若计算值 > 50mm，标记为超规格警告，建议改用双层缓冲或多腔体设计。

---

## F-05 湿度修正系数

**公式 ID**：F-05  
**用途**：瓦楞纸板的 BCT 随湿度显著下降，需对目标 BCT 进行修正。

### 主公式

```
humidity_correction_factor = base_factor × (1 - humidity_decay_rate × excess_humidity_pct)
```

其中：
- `excess_humidity_pct = MAX(0, storage_humidity_pct - 50)`（超出 50% 的部分）
- `base_factor` 和 `humidity_decay_rate` 由运输模式决定

### 参数表

| 运输模式 | base_factor | humidity_decay_rate |
|--------|------------|-------------------|
| sea    | 1.00       | 0.012（海运高湿重要）  |
| land   | 1.00       | 0.008             |
| air    | 1.00       | 0.005（机舱湿度可控）  |
| multimodal | 1.00  | 0.010             |

**边界约束**：`humidity_correction_factor` 最小值为 0.50（即 BCT 最多折减 50%）

**默认值**：若 `storage_humidity_pct` 未提供，默认使用 70%，并在结果中标注为估算值。

### 计算示例

```
输入：storage_humidity_pct = 80, transport_mode = "sea"
excess_humidity_pct = MAX(0, 80 - 50) = 30
humidity_correction_factor = 1.00 × (1 - 0.012 × 30) = 1.00 × (1 - 0.36) = 0.64

adjusted_bct_n = target_bct_n / 0.64
```

---

## F-06 纸板厚度与 ECT 换算

**公式 ID**：F-06  
**用途**：在选定楞型后，验证所选材料的 ECT 是否满足要求，或反向验证楞型选择。

### 验证流程

```
1. 从配置表取候选材料的 actual_ect_n_per_m
2. 代入 McKee 公式计算可提供的 BCT：
   available_bct = 5.87 × actual_ect × √(Z × t)
3. 比较 available_bct 与 adjusted_bct_n：
   裕量 = (available_bct - adjusted_bct_n) / adjusted_bct_n × 100%
   
   裕量 < 0%：不合格，换更高规格材料
   裕量 0 ~ 20%：最优区间（得分最高）
   裕量 20 ~ 50%：可用，有冗余（扣部分强度裕量分）
   裕量 > 50%：过度设计（建议降级）
```

---

## 附录 A 参数查找表

### A-1 楞型技术参数速查

| 楞型 | 厚度(mm) | 楞数(个/m) | 抗垂直压 | 抗平压 | 典型 ECT 范围 (kN/m) |
|-----|---------|-----------|---------|------|-------------------|
| E   | 1.5     | 290       | 低      | 高   | 3.0 ~ 5.0         |
| B   | 2.5     | 150       | 中      | 中   | 4.5 ~ 7.0         |
| C   | 3.6     | 130       | 中高    | 中   | 5.5 ~ 9.0         |
| A   | 4.7     | 120       | 高      | 低   | 6.0 ~ 10.0        |
| BC  | 7.0     | —         | 很高    | 高   | 9.0 ~ 15.0        |
| AB  | 8.0     | —         | 极高    | 高   | 12.0 ~ 20.0       |

### A-2 常用缓冲材料规格（标准厚度）

| 材料    | 标准厚度规格(mm)             | 密度(kg/m³) | 压缩率 |
|--------|--------------------------|-----------|------|
| EPE 珍珠棉 | 5, 10, 15, 20, 25, 30, 40, 50 | 15~30 | 40% |
| EVA 泡棉 | 5, 10, 15, 20, 25, 30    | 30~60  | 30% |
| 蜂窝纸板  | 10, 15, 20, 25, 30       | 25~45  | 50% |
| 聚氨酯   | 20, 25, 30, 40, 50       | 20~80  | 35% |
