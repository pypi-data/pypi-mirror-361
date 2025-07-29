# 表格组件 (TableWidget)

TableWidget 是用于展示结构化数据的专业组件，支持表头、状态单元格、条纹样式、索引列等多种功能，是数据报告中的核心组件。

## 🚀 快速开始

```python
from email_widget.widgets import TableWidget

# 创建基本表格
table = TableWidget()
table.set_headers(["姓名", "年龄", "部门"])
table.add_row(["张三", "28", "技术部"])
table.add_row(["李四", "32", "销售部"])
```

<div style="background: #ffffff; border: 1px solid #e1dfdd; border-radius: 4px; padding: 16px; margin: 16px 0;">
    <table style="width: 100%; border-collapse: collapse;">
        <thead>
            <tr style="background: #f8f9fa;">
                <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e9ecef; font-weight: 600;">姓名</th>
                <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e9ecef; font-weight: 600;">年龄</th>
                <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e9ecef; font-weight: 600;">部门</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">张三</td>
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">28</td>
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">技术部</td>
            </tr>
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">李四</td>
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">32</td>
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">销售部</td>
            </tr>
        </tbody>
    </table>
</div>

## 📊 基本用法

### 设置表头和数据

```python
# 设置表头
table = TableWidget()
table.set_headers(["项目", "状态", "进度", "负责人"])

# 添加数据行
table.add_row(["用户系统", "开发中", "75%", "张工"])
table.add_row(["支付模块", "测试中", "90%", "李工"])
table.add_row(["数据统计", "已完成", "100%", "王工"])

# 批量添加行
rows_data = [
    ["项目A", "进行中", "60%", "员工A"],
    ["项目B", "已完成", "100%", "员工B"],
    ["项目C", "计划中", "0%", "员工C"]
]
table.add_rows(rows_data)
```

### 设置表格标题

```python
table = TableWidget()
table.set_title("项目进度统计表")
table.set_headers(["项目名称", "完成状态"])
table.add_row(["项目Alpha", "75%"])
```

<div style="background: #ffffff; border: 1px solid #e1dfdd; border-radius: 4px; padding: 16px; margin: 16px 0;">
    <h3 style="margin: 0 0 16px 0; font-size: 18px; font-weight: 600; color: #323130;">项目进度统计表</h3>
    <table style="width: 100%; border-collapse: collapse;">
        <thead>
            <tr style="background: #f8f9fa;">
                <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e9ecef; font-weight: 600;">项目名称</th>
                <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e9ecef; font-weight: 600;">完成状态</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">项目Alpha</td>
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">75%</td>
            </tr>
        </tbody>
    </table>
</div>

## 🎨 样式配置

### 条纹样式

```python
# 启用条纹样式
table = TableWidget()
table.set_striped(True)
table.set_headers(["序号", "产品", "销量"])
table.add_rows([
    ["1", "产品A", "1,200"],
    ["2", "产品B", "980"],
    ["3", "产品C", "1,500"],
    ["4", "产品D", "750"]
])
```

<div style="background: #ffffff; border: 1px solid #e1dfdd; border-radius: 4px; padding: 16px; margin: 16px 0;">
    <table style="width: 100%; border-collapse: collapse;">
        <thead>
            <tr style="background: #f8f9fa;">
                <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e9ecef; font-weight: 600;">序号</th>
                <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e9ecef; font-weight: 600;">产品</th>
                <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e9ecef; font-weight: 600;">销量</th>
            </tr>
        </thead>
        <tbody>
            <tr style="background: #ffffff;">
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">1</td>
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">产品A</td>
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">1,200</td>
            </tr>
            <tr style="background: #f8f9fa;">
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">2</td>
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">产品B</td>
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">980</td>
            </tr>
            <tr style="background: #ffffff;">
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">3</td>
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">产品C</td>
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">1,500</td>
            </tr>
            <tr style="background: #f8f9fa;">
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">4</td>
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">产品D</td>
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">750</td>
            </tr>
        </tbody>
    </table>
</div>

### 边框和索引列

```python
# 显示边框和索引列
table = TableWidget()
table.set_show_border(True)
table.set_show_index(True)
table.set_headers(["任务", "状态"])
table.add_rows([
    ["数据备份", "完成"],
    ["系统更新", "进行中"],
    ["安全检查", "待开始"]
])
```

<div style="background: #ffffff; border: 1px solid #e1dfdd; border-radius: 4px; padding: 16px; margin: 16px 0;">
    <table style="width: 100%; border-collapse: collapse; border: 1px solid #e1dfdd;">
        <thead>
            <tr style="background: #f8f9fa;">
                <th style="padding: 12px; text-align: left; border: 1px solid #e1dfdd; font-weight: 600;">索引</th>
                <th style="padding: 12px; text-align: left; border: 1px solid #e1dfdd; font-weight: 600;">任务</th>
                <th style="padding: 12px; text-align: left; border: 1px solid #e1dfdd; font-weight: 600;">状态</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="padding: 12px; border: 1px solid #e1dfdd; background: #f8f9fa; font-weight: 600;">1</td>
                <td style="padding: 12px; border: 1px solid #e1dfdd;">数据备份</td>
                <td style="padding: 12px; border: 1px solid #e1dfdd;">完成</td>
            </tr>
            <tr>
                <td style="padding: 12px; border: 1px solid #e1dfdd; background: #f8f9fa; font-weight: 600;">2</td>
                <td style="padding: 12px; border: 1px solid #e1dfdd;">系统更新</td>
                <td style="padding: 12px; border: 1px solid #e1dfdd;">进行中</td>
            </tr>
            <tr>
                <td style="padding: 12px; border: 1px solid #e1dfdd; background: #f8f9fa; font-weight: 600;">3</td>
                <td style="padding: 12px; border: 1px solid #e1dfdd;">安全检查</td>
                <td style="padding: 12px; border: 1px solid #e1dfdd;">待开始</td>
            </tr>
        </tbody>
    </table>
</div>

## 🎯 状态单元格

TableWidget 支持特殊的状态单元格，可以显示彩色的状态信息：

```python
from email_widget.widgets import TableWidget, TableCell
from email_widget.core.enums import StatusType

table = TableWidget()
table.set_headers(["服务", "状态", "响应时间"])
table.add_row([
    "Web服务",
    TableCell("正常", StatusType.SUCCESS),
    "145ms"
])
table.add_row([
    "数据库",
    TableCell("警告", StatusType.WARNING),
    "892ms"
])
table.add_row([
    "缓存服务",
    TableCell("故障", StatusType.ERROR),
    "超时"
])
```

<div style="background: #ffffff; border: 1px solid #e1dfdd; border-radius: 4px; padding: 16px; margin: 16px 0;">
    <table style="width: 100%; border-collapse: collapse;">
        <thead>
            <tr style="background: #f8f9fa;">
                <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e9ecef; font-weight: 600;">服务</th>
                <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e9ecef; font-weight: 600;">状态</th>
                <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e9ecef; font-weight: 600;">响应时间</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">Web服务</td>
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef; color: #107c10; font-weight: 600;">正常</td>
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">145ms</td>
            </tr>
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">数据库</td>
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef; color: #ff8c00; font-weight: 600;">警告</td>
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">892ms</td>
            </tr>
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">缓存服务</td>
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef; color: #d13438; font-weight: 600;">故障</td>
                <td style="padding: 12px; border-bottom: 1px solid #e9ecef;">超时</td>
            </tr>
        </tbody>
    </table>
</div>

### 状态类型说明

| 状态类型 | 颜色 | 适用场景 |
|---------|------|----------|
| `StatusType.SUCCESS` | 绿色 (#107c10) | 成功、正常、通过 |
| `StatusType.WARNING` | 橙色 (#ff8c00) | 警告、注意、待处理 |
| `StatusType.ERROR` | 红色 (#d13438) | 错误、失败、异常 |
| `StatusType.INFO` | 蓝色 (#0078d4) | 信息、提示、中性 |

## 📋 完整示例

### 系统监控表格

```python
from email_widget import Email
from email_widget.widgets import TableWidget, TableCell
from email_widget.core.enums import StatusType

# 创建邮件
email = Email("系统监控报告")

# 创建监控表格
monitor_table = TableWidget()
monitor_table.set_title("系统服务状态")
monitor_table.set_headers(["服务名称", "状态", "CPU使用率", "内存使用率", "最后检查时间"])
monitor_table.set_striped(True)
monitor_table.set_show_index(True)

# 添加监控数据
monitor_table.add_rows([
    ["Web服务器", TableCell("运行", StatusType.SUCCESS), "23%", "45%", "2024-01-15 10:30"],
    ["数据库", TableCell("警告", StatusType.WARNING), "78%", "67%", "2024-01-15 10:29"],
    ["Redis缓存", TableCell("正常", StatusType.SUCCESS), "12%", "34%", "2024-01-15 10:30"],
    ["消息队列", TableCell("故障", StatusType.ERROR), "0%", "0%", "2024-01-15 09:45"],
    ["文件服务", TableCell("正常", StatusType.SUCCESS), "15%", "28%", "2024-01-15 10:30"]
])

email.add_widget(monitor_table)
```

### 销售数据表格

```python
# 创建销售数据表格
sales_table = TableWidget()
sales_table.set_title("月度销售数据")
sales_table.set_headers(["产品名称", "销售数量", "销售额", "增长率", "状态"])
sales_table.set_show_border(True)

# 添加销售数据
sales_table.add_rows([
    ["智能手机", "1,250", "¥2,500,000", "+15%", TableCell("超额", StatusType.SUCCESS)],
    ["平板电脑", "680", "¥1,360,000", "+8%", TableCell("达标", StatusType.SUCCESS)],
    ["笔记本电脑", "420", "¥2,100,000", "-5%", TableCell("待改进", StatusType.WARNING)],
    ["智能手表", "890", "¥1,780,000", "+25%", TableCell("优秀", StatusType.SUCCESS)]
])

email.add_widget(sales_table)
```

## ⚙️ API 参考

### 基本配置方法

| 方法 | 参数 | 说明 | 示例 |
|------|------|------|------|
| `set_title()` | `title: str` | 设置表格标题 | `.set_title("数据表")` |
| `set_headers()` | `headers: List[str]` | 设置表头 | `.set_headers(["列1", "列2"])` |
| `add_row()` | `row: List[Union[str, TableCell]]` | 添加单行数据 | `.add_row(["值1", "值2"])` |
| `add_rows()` | `rows: List[List[Union[str, TableCell]]]` | 批量添加行 | `.add_rows([["a", "b"], ["c", "d"]])` |
| `clear_rows()` | 无 | 清空所有数据行 | `.clear_rows()` |

### 样式配置方法

| 方法 | 参数 | 说明 | 默认值 |
|------|------|------|--------|
| `set_striped()` | `striped: bool` | 设置条纹样式 | `False` |
| `set_show_border()` | `show: bool` | 显示边框 | `False` |
| `set_show_index()` | `show: bool` | 显示索引列 | `False` |
| `set_max_width()` | `width: str` | 设置最大宽度 | `"100%"` |

### TableCell 类

```python
# 创建状态单元格
cell = TableCell("文本内容", StatusType.SUCCESS)

# 或者使用普通字符串
cell = "普通文本"
```

## 🎯 最佳实践

### 1. 合理使用状态单元格
```python
# 推荐：为状态相关的列使用状态单元格
table.add_row([
    "任务名称",
    TableCell("已完成", StatusType.SUCCESS),  # 状态列
    "2024-01-15"  # 普通文本列
])
```

### 2. 保持数据一致性
```python
# 推荐：确保每行数据列数与表头一致
headers = ["姓名", "年龄", "部门"]
table.set_headers(headers)
table.add_row(["张三", "28", "技术部"])  # 3列数据匹配3个表头
```

### 3. 适当使用样式增强可读性
```python
# 推荐：大数据表格使用条纹样式
large_table = TableWidget()
large_table.set_striped(True)
large_table.set_show_index(True)  # 便于引用特定行
```

### 4. 控制表格宽度避免布局问题
```python
# 推荐：为包含大量列的表格设置最大宽度
wide_table = TableWidget()
wide_table.set_max_width("800px")
```

## 🚨 注意事项

1. **列数一致性**: 确保每行数据的列数与表头列数一致
2. **内容长度**: 避免单元格内容过长影响布局
3. **状态使用**: 合理使用状态单元格，不要滥用颜色
4. **性能考虑**: 大数据量时考虑分页或分表显示

---

**下一步**: 了解 [图表组件](chart-widget.md) 学习如何展示可视化数据。 