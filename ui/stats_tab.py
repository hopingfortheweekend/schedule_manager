"""
数据统计看板：折线图展示完成 vs 全部趋势，支持切换时间范围。
"""
import tkinter as tk
from tkinter import ttk
import datetime
from collections import defaultdict

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

# 设置中文字体（Windows 用微软雅黑）
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class StatsTab(ttk.Frame):
    PERIODS = {
        "过去 4 周": ("week", 4),
        "过去 3 个月": ("month", 3),
        "过去 12 个月": ("month", 12),
    }

    def __init__(self, parent, data_store):
        super().__init__(parent)
        self.data_store = data_store
        self.current_mode = "week"   # week | month
        self.current_num = 4

        # 控制栏
        ctrl = ttk.Frame(self)
        ctrl.pack(fill="x", padx=10, pady=5)
        ttk.Label(ctrl, text="时间范围:").pack(side=tk.LEFT)
        for label, (mode, num) in self.PERIODS.items():
            ttk.Button(ctrl, text=label,
                       command=lambda m=mode, n=num: self._switch(m, n)
                       ).pack(side=tk.LEFT, padx=2)

        # 完成率概览
        self.summary_label = ttk.Label(self, text="", font=("", 11))
        self.summary_label.pack(pady=(5, 0))

        # matplotlib 图表
        self.fig = Figure(figsize=(6, 3.5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)

        self.refresh()

    def refresh(self):
        self._draw()

    def _switch(self, mode, num):
        self.current_mode = mode
        self.current_num = num
        self._draw()

    # ── 数据聚合 ──────────────────────────────

    def _aggregate(self):
        """根据当前时间范围聚合数据，返回 (labels, totals, dones)"""
        today = datetime.date.today()

        if self.current_mode == "week":
            delta = datetime.timedelta(weeks=self.current_num)
            start = today - delta
            # 按周分桶
            buckets = []
            for i in range(self.current_num):
                week_end = start + datetime.timedelta(weeks=i + 1)
                week_start = start + datetime.timedelta(weeks=i)
                buckets.append((week_start, week_end))
            label_fmt = lambda s, e: f"{s.month}/{s.day}-{e.month}/{e.day}"
        else:
            # month
            delta = datetime.timedelta(days=self.current_num * 31)
            start = today - delta
            buckets = []
            for i in range(self.current_num):
                # 每月近似
                bs = start + datetime.timedelta(days=i * 31)
                be = start + datetime.timedelta(days=(i + 1) * 31)
                buckets.append((bs, be))
            label_fmt = lambda s, e: f"{s.month}月"

        labels = []
        totals = []
        dones = []

        tasks = self.data_store.data.get("tasks", {})
        for bs, be in buckets:
            labels.append(label_fmt(bs, be))
            t_total = 0
            t_done = 0
            for date_str, t_list in tasks.items():
                try:
                    d = datetime.date.fromisoformat(date_str)
                except ValueError:
                    continue
                if bs <= d < be:
                    t_total += len(t_list)
                    t_done += sum(1 for t in t_list if t.get("done"))
            totals.append(t_total)
            dones.append(t_done)

        return labels, totals, dones

    # ── 绘图 ──────────────────────────────────

    def _draw(self):
        labels, totals, dones = self._aggregate()

        self.ax.clear()
        x = range(len(labels))

        self.ax.plot(x, totals, "o-", color="#4D96FF", linewidth=2,
                     markersize=6, label="全部日程")
        self.ax.plot(x, dones, "o-", color="#6BCB77", linewidth=2,
                     markersize=6, label="已完成")

        # 数值标注
        for i in x:
            self.ax.annotate(str(totals[i]), (i, totals[i]),
                             textcoords="offset points", xytext=(0, 10),
                             fontsize=8, ha="center", color="#4D96FF")
            if dones[i] > 0:
                self.ax.annotate(str(dones[i]), (i, dones[i]),
                                 textcoords="offset points", xytext=(0, -14),
                                 fontsize=8, ha="center", color="#2d8a4e")

        self.ax.set_xticks(list(x))
        self.ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=8)
        self.ax.set_ylabel("日程数量")
        self.ax.legend(loc="upper left")
        self.ax.set_ylim(bottom=0)
        self.ax.grid(axis="y", alpha=0.3)

        self.fig.tight_layout()
        self.canvas.draw()

        # 汇总
        grand_total = sum(totals)
        grand_done = sum(dones)
        rate = f"{grand_done / grand_total * 100:.0f}%" if grand_total > 0 else "暂无数据"
        self.summary_label.config(
            text=f"总日程: {grand_total}  ·  已完成: {grand_done}  ·  完成率: {rate}")
