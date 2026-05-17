# 最终设计方案输出格式规范

本文档定义 Step 4（方案整理智能体）生成最终方案文档的模板与字段说明。

---

## 输出格式

使用 Markdown 格式，结构如下：

---

```markdown
# 外包装设计方案
**方案编号**：{design_id}  
**设计日期**：{YYYY-MM-DD}  
**产品名称**：{product_name}  
**状态**：{完成 / 部分完成（含警告）}

---

## 一、申请单摘要

| 参数 | 值 |
|------|-----|
| 产品尺寸（L×W×H） | {length}mm × {width}mm × {height}mm |
| 产品重量 | {weight}kg |
| 单箱装配数量 | {quantity} 件 |
| 运输方式 | {transport_mode} |
| 易碎等级 | {fragility_level} |
| 特殊要求 | {special_requirements 或"无"} |

---

## 二、箱体设计方案

**推荐箱型**：{box_id} — {box_type}型纸箱  
**内尺寸**：{inner_L}mm × {inner_W}mm × {inner_H}mm  
**外尺寸**：{outer_L}mm × {outer_W}mm × {outer_H}mm  
**最大承重**：{max_weight_capacity}kg  
**匹配得分**：{match_score}  

**选型依据**：
{selection_rationale}

> 备选方案：{alternatives 简要描述，如无则写"—"}

---

## 三、材料设计方案

### 外箱材料
| 参数 | 值 |
|------|-----|
| 材料编号 | {material_id} |
| 材料描述 | {description} |
| ECT（边压强度） | {ect} N/m |
| 箱体抗压强度（BCT） | {bcl} N |
| 材料厚度 | {thickness}mm |

### 缓冲材料
| 参数 | 值 |
|------|-----|
| 材料编号 | {cushion_material_id} |
| 材料描述 | {cushion_description} |
| 厚度 | {cushion_thickness}mm |
| 放置方式 | {placement} |

### 关键计算参数
- 设计跌落高度：{calculated_drop_height}m
- G值（脆值）：{fragility_g_value}
- 缓冲效率：{cushion_efficiency}
- 安全系数：{safety_factor}

**选材依据**：
{selection_rationale}

{如需人工复核，显示：}
> ⚠️ **人工复核提示**：{manual_review_notes}

---

## 四、方案分析

### 4.1 堆叠分析

{如分析成功：}
| 分析项 | 结果 |
|--------|------|
| 最大可堆叠层数 | {max_stacking_layers} 层 |
| 建议堆叠层数 | {recommended_stacking_layers} 层 |
| 静载荷极限 | {static_load_limit}kg |
| 安全余量 | {safety_margin}% |
| 稳定性评分 | {stability_score} |
| 预测失效模式 | {failure_mode} |

**建议**：{recommendations}

{如分析失败：}
> ⚠️ 堆叠分析数据不可用（{error_message}），建议手动委托实验室测试。

---

### 4.2 成本分析

{如分析成功：}
| 成本构成 | 金额（元/套） |
|----------|--------------|
| 外箱 | {outer_box_cny} |
| 缓冲材料 | {cushioning_cny} |
| 附属材料 | {accessories_cny} |
| **合计** | **{total_per_unit_cny}** |

{如设置了目标成本：}
**与目标成本对比**：{meets_target_cost ? "✓ 达标" : "✗ 超标"} （{cost_vs_target_percent}%）

**优化建议**：{optimization_suggestions 或"—"}

{如分析失败：}
> ⚠️ 成本分析数据不可用，请联系采购部门手动估价。

---

### 4.3 相似历史方案参考

{如检索到相似方案：}
{对每个相似案例：}
**案例 {n}**：{design_id} — {product_name}（相似度 {similarity_score}）  
- 相似要素：{key_similarities}  
- 历史结果：{outcome}  
- 经验参考：{lessons_learned}

**综合建议**：{recommendation}

{如未检索到相似方案：}
> 未找到相似历史案例，本次为全新设计。

---

## 五、执行建议与后续步骤

1. **打样验证**：按本方案尺寸制作打样，进行 ISTA/ASTM 跌落测试
2. **认证要求**：{certifications_required 如有，列出需要准备的认证}
3. **供应商推荐**：参考相似案例 {design_id} 的供应商名单
4. **注意事项**：{special_requirements 中提及的注意事项}

---

## 六、设计过程日志

{如有警告或降级处理，列出：}
| 步骤 | 日志类型 | 说明 |
|------|----------|------|
| {step} | {INFO/WARN/ERROR} | {message} |

{如全程无异常，写"本次设计全流程执行正常，无异常记录。"}

---

*本方案由外包装设计智能体自动生成，最终方案须经专业工程师审核确认后方可投入量产。*
```

---

## 输出字段缺失处理规则

| 情况 | 处理方式 |
|------|----------|
| 某分析步骤失败 | 对应章节显示 ⚠️ 提示，内容替换为"数据不可用" |
| 可选字段为空 | 显示"—"或"无" |
| 数值精度 | 成本保留 2 位小数；得分/比例保留 2 位小数；尺寸取整至 mm |
| 长文本字段（rationale 等） | 直接引用子智能体输出，不二次加工 |

## 文件格式

默认输出为 Markdown（`.md`），便于在线预览和版本管理。
如用户要求，可由方案整理智能体额外生成 Word（`.docx`）格式。
