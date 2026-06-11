# 轻简日程管理 (Light Schedule Manager)

一个基于 Python Tkinter 的本地日程管理工具。将大项目拆解为可执行的步骤，在日历上直观看到每个截止日期的时间分布，帮助拖延症患者一眼看清"我还有多少时间"。

## ✨ 功能

- **每日任务管理** — 添加、切换状态、双击编辑/删除每日待办事项
- **长期项目拆解** — 将大项目拆分为子步骤，每个步骤可设定独立的截止日期，支持编辑/删除
- **当日汇总** — 长期项目中截止日期为当日的步骤，自动显示在"每日任务"页面
- **日历可视化** — 所有任务日期和项目步骤 DDL 以彩色标记显示在日历上，按紧急程度区分颜色（逾期红色 → 3天内橙色 → 7天内黄色 → 更远绿色），点击任意日期查看详情
- **数据统计看板** — 折线图展示过去 N 周/月的完成 vs 全部趋势，含完成率概览
- **CSV 数据导出** — 按时间范围筛选并导出为 CSV 文件，支持快捷范围（本月/近3月/全部）
- **本地数据存储** — JSON 文件持久化，数据完全由你掌控，无需联网

## 🛠 技术栈

| 层面 | 技术 |
|------|------|
| 语言 | Python 3.11 |
| GUI 框架 | Tkinter + ttk |
| 日历组件 | tkcalendar |
| 数据图表 | matplotlib |
| 数据存储 | JSON 本地文件 |
| 测试 | pytest |

## 🚀 快速开始

### 环境要求

- Python >= 3.8
- pip

### 安装 & 运行

```bash
# 1. 克隆项目
git clone <repo-url>
cd Schedule_management

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行
python main.py
```

### 运行测试

```bash
pytest tests/ -v
```

## 📁 项目结构

```
Schedule_management/
├── main.py               # 入口文件
├── data_store.py          # 数据层（JSON 读写 + 增删改查）
├── ui/
│   ├── task_tab.py        # 每日任务页面
│   ├── project_tab.py     # 长期项目页面
│   ├── calendar_tab.py    # 日历视图页面
│   ├── stats_tab.py       # 数据统计看板
│   └── dialogs.py         # 编辑/删除弹窗
├── utils/
│   ├── logger.py          # 日志工具
│   └── export.py          # CSV 导出
├── tests/
│   └── test_data_store.py # 单元测试（15 个用例）
├── docs/
│   └── PRD.md             # 产品需求文档
├── schedule_data.json     # 数据文件
├── requirements.txt       # 依赖声明
└── README.md
```

## 📝 使用说明

| 标签页 | 操作方式 |
|--------|----------|
| 每日任务 | 点击"添加任务"，单击状态标记切换完成，双击编辑或删除 |
| 长期项目 | 点击"添加项目"，双击项目进入步骤管理，选中后"删除项目" |
| 日历视图 | 点击日期查看详情，彩色标记区分紧急程度 |
| 数据统计 | 点击时间范围按钮切换图表，查看完成率趋势 |
| 导出数据 | 点击右上角"导出数据"，选范围 → 保存为 CSV |

## 📄 License

MIT
