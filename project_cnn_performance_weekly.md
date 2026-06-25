---
name: project-cnn-performance-weekly
description: CNN Performance Weekly 周度数据复盘看板，Streamlit + 暖色纸质主题 + 导出HTML
metadata:
  node_type: memory
  type: project
  originSessionId: 7ab7dfa8-6ef4-4c4c-9984-514a7a59f37d
---

# CNN Performance Weekly 周度数据复盘看板

**项目路径**：`C:\Users\a952462\cnn-performance-weekly`
**当前版本**：`ed36387`（2026-06-25）
**运行端口**：8503（`streamlit run app.py --server.port 8503`）

## 架构

```
app.py              # 主入口，顶部栏+导航+侧边栏+4层内容
config.py           # 品牌色(THEME_*)、列名映射、评分参数、渠道配置
data.py             # 数据读取（fuzzy match、多编码、XLSX/CSV）
scoring.py          # 综合评分算法（触达30%+CTR40%+GC30%）
components.py       # KPI卡片、section_header、_fmt_number等可复用组件
styles.py           # 暖色纸质主题CSS，全部使用config常量
export.py           # 导出HTML功能（导入components._fmt_number）
llm_service.py      # LLM AI分析服务（dirtyjson修复JSON解析）
setup_and_run.bat   # 一键启动脚本
favicon.png         # 网页图标
mcdonalds.png       # 麦当劳logo
tabs/
  tab_summary.py    # Layer 1: Executive Summary（4个日均KPI+DAU趋势图）
  tab_operational.py # Layer 2: Operational分析（AARR/常规堆积+分渠道堆积+分渠道明细）
  tab_bu.py         # Layer 3: BU分析（4个排行榜+总览表，无图表）
  tab_plan.py       # Layer 4: Plan分析（TOP4卡片+药丸豆腐块+AI解读+删除功能）
```

## 设计风格

参考 `ITO Traffic Operating Framework_V2.0.html`：
- 顶部栏：红色渐变+金色M logo，`position: fixed` 固定，badge显示所选日期范围
- 导航栏：锚点跳转，pill圆角按钮，hover浅粉底红字
- 主题色：深红 #a8001a、金色 #FFBC0D、墨色 #2b2620
- 背景：暖纸质 #f4efe6，卡片 #fffdf8
- 表格：深红表头 #a8001a，交替行 #fcfaf3
- 指标命名：`指标名称（日均）`格式，Plan数不加日均
- 豆腐块：药丸样式，#F8F7F5底色，3px 10px内边距，12px字号

## 关键设计决策

1. **单页滚动**：4个section在同一页面，导航用锚点跳转
2. **固定header**：用 `streamlit.components.html()` 执行JS，把topbar和nav移到body层级
3. **侧边栏固定**：隐藏折叠按钮，宽度280px，header左边距280px
4. **日期范围**：默认上一个自然周，限定在数据范围内
5. **Target默认50000**，target线统一黑色，Target为0时显示"/"
6. **Plotly导出**：用 `to_json()`/`from_json()` 序列化（避免Plotly 6.6的deepcopy二进制问题）
7. **每个图表自带Plotly CDN引用**：`include_plotlyjs='cdn'`（避免版本号错误导致图表不显示）
8. **日均计算**：动态根据筛选日期范围的天数，非写死7天
9. **顶部栏badge**：用JS动态更新为所选日期范围
10. **Plan分析TOP4**：每个渠道显示4个Plan卡片，支持删除后自动补充
11. **AI解读3维度**：综合评分/CTR/Sales，每个维度TOP4都有AI解读
12. **短信渠道**：在Plan分析中排除（PLAN_CHANNELS），其他地方保留

## 已完成

- [x] 4层框架完整实现
- [x] 暖色纸质主题，全部使用config常量
- [x] 固定顶部栏+导航栏
- [x] 锚点跳转+scroll-margin-top补偿
- [x] 侧边栏固定不折叠
- [x] 日期范围默认+限定
- [x] Target线统一黑色
- [x] KPI卡片格式化（K/M），全部日均
- [x] 导出HTML功能（完整图表+表格+KPI）
- [x] BU排行榜（4个：Plan数/触达/CTR/Sales，带奖牌）
- [x] Plan TOP4卡片（药丸豆腐块+文案+两列布局）
- [x] 分渠道堆积图（含渠道占比百分比）
- [x] setup_and_run.bat一键启动
- [x] Plan卡片删除功能（移除按钮+自动补充+重置按钮）
- [x] AI解读支持3维度（综合评分/CTR/Sales）
- [x] AI解读prompt优化（核心亮点/可借鉴点/可优化，30字）
- [x] AI解读JSON解析4层兜底（dirtyjson→标准json→正则→空列表）
- [x] Target为0时显示"/"
- [x] 堆积柱状图显示具体数值（柱子顶部）+百分比（柱子内部）
- [x] 短信渠道在Plan分析中排除
- [x] 渠道总结功能（为什么好+内容框架XX+XX+XX）

## Plan删除功能

- 每个卡片下方有"移除"按钮
- 删除后后面的Plan自动顶上，重新排序（1,2,3,4）
- 有"🔄 重置"按钮恢复所有被删除的Plan
- 切换渠道/维度后删除状态保留（session_state）
- 导出HTML会过滤掉被删除的Plan，但不显示删除按钮
- AI解读也会过滤被删除的Plan，只解读当前显示的4个

## AI解读配置

**Prompt结构**（llm_service.py）：
- 3个维度：核心亮点、可借鉴点、可优化（可选）
- 字数：30字左右
- 可优化不是必须输出项，有就输出，没有留空
- 同一天两条相同文案可能是不同人群投放，非重复

**输出字段**：
- `highlight` - 核心亮点（表现好的主要原因）
- `reference` - 可借鉴点（值得借鉴复用的点）
- `optimize` - 可优化（可选，无则空字符串）

**Key格式**：`{Plan ID}_{渠道}_{维度}`（如 `P001_APP-Push_ctr`）

**调用量**：渠道数 × 3维度 × 4条 = 36条（3渠道×3×4）

**渠道总结**：
- 每个渠道独立总结，放在渠道筛选下方
- 两个维度：
  - **为什么好**（30-50字）：抽象TOP4 Plan的共同成功因素
  - **内容框架**（XX+XX+XX）：提炼可复用的内容框架模板
- 调用量：渠道数 × 1条 = 3条（3渠道×1）

## 渠道配置

- **全局CHANNELS**：APP Push、企微1v1、短信、微信小程序订阅消息
- **Plan分析PLAN_CHANNELS**：APP Push、企微1v1、微信小程序订阅消息（排除短信）
- 短信在Operational分析、侧边栏筛选等地方保留

## 待优化

- [ ] 导出HTML每个图表都带Plotly CDN引用，文件偏大，可优化为head中统一引用
- [ ] 导出HTML的logo用base64内嵌，可考虑压缩

## 常见问题

1. **图表不显示**：检查Plotly CDN版本号是否正确
2. **数据线在0位置**：Plotly 6.6的deepcopy会转二进制，用to_json()替代
3. **侧边栏隐藏后回不来**：不要隐藏header，只调整透明度
4. **日期类型不匹配**：st.date_input返回Python date，需转pd.Timestamp
5. **JSON解析失败**：使用dirtyjson库+正则提取兜底
6. **AI解读token消耗**：每个渠道×3维度×4条，共36条
