"""
数据导出工具：将日程数据导出为 CSV 文件。
"""
import csv
import datetime
from tkinter import filedialog, messagebox


def export_csv(data_store, parent):
    """弹出日期选择窗口，导出 CSV"""
    ExportDialog(parent, data_store)


class ExportDialog:
    def __init__(self, parent, data_store):
        import tkinter as tk
        from tkinter import ttk

        self.data_store = data_store
        self.top = tk.Toplevel(parent)
        self.top.title("导出数据")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()

        # 日期输入
        ttk.Label(self.top, text="起始日期 (YYYY-MM-DD):").grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        self.start_var = tk.StringVar()
        ttk.Entry(self.top, textvariable=self.start_var, width=20).grid(row=0, column=1, padx=10, pady=(10, 0))

        ttk.Label(self.top, text="结束日期 (YYYY-MM-DD):").grid(row=1, column=0, padx=10, pady=(5, 0), sticky="w")
        self.end_var = tk.StringVar()
        ttk.Entry(self.top, textvariable=self.end_var, width=20).grid(row=1, column=1, padx=10, pady=(5, 0))

        # 快捷按钮
        qf = ttk.LabelFrame(self.top, text="快捷范围", padding=5)
        qf.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        today = datetime.date.today()
        ttk.Button(qf, text="本月", command=lambda: self._quick(
            today.replace(day=1),
            today)).pack(side=tk.LEFT, padx=2)
        ttk.Button(qf, text="近 3 个月", command=lambda: self._quick(
            today - datetime.timedelta(days=90),
            today)).pack(side=tk.LEFT, padx=2)
        ttk.Button(qf, text="全部", command=lambda: self._quick(None, None)).pack(side=tk.LEFT, padx=2)

        # 导出按钮
        ttk.Button(self.top, text="选择保存位置并导出", command=self._do_export).grid(
            row=3, column=0, columnspan=2, pady=10)

        self.top.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        x = parent.winfo_rootx() + (pw - self.top.winfo_width()) // 2
        y = parent.winfo_rooty() + (ph - self.top.winfo_height()) // 2
        self.top.geometry(f"+{x}+{y}")

    def _quick(self, start, end):
        if start:
            self.start_var.set(str(start))
        else:
            self.start_var.set("")
        if end:
            self.end_var.set(str(end))
        else:
            self.end_var.set("")

    def _do_export(self):
        start_str = self.start_var.get().strip()
        end_str = self.end_var.get().strip()

        try:
            start = datetime.date.fromisoformat(start_str) if start_str else datetime.date.min
            end = datetime.date.fromisoformat(end_str) if end_str else datetime.date.max
        except ValueError:
            messagebox.showerror("格式错误", "日期格式应为 YYYY-MM-DD", parent=self.top)
            return

        # 收集数据
        rows = []
        # 每日任务
        for date_str, t_list in self.data_store.data.get("tasks", {}).items():
            try:
                d = datetime.date.fromisoformat(date_str)
            except ValueError:
                continue
            if start <= d <= end:
                for t in t_list:
                    rows.append({
                        "类型": "每日任务",
                        "名称": t["task"],
                        "所属项目": "",
                        "截止日期": date_str,
                        "完成状态": "已完成" if t.get("done") else "未完成",
                    })

        # 项目步骤
        for proj_name, proj_data in self.data_store.data.get("projects", {}).items():
            for step in proj_data.get("steps", []):
                dl_str = step.get("deadline", "")
                include = False
                if not dl_str:
                    include = (start <= datetime.date.min)  # 无日期的，只在"全部"时包含
                else:
                    try:
                        dl = datetime.date.fromisoformat(dl_str)
                        include = (start <= dl <= end)
                    except ValueError:
                        include = not start_str  # 无有效日期的只在"全部"导出

                if include:
                    rows.append({
                        "类型": "项目步骤",
                        "名称": step["step"],
                        "所属项目": proj_name,
                        "截止日期": dl_str,
                        "完成状态": "已完成" if step.get("done") else "未完成",
                    })

        if not rows:
            messagebox.showinfo("提示", "所选范围内无日程记录", parent=self.top)
            return

        # 文件保存
        filepath = filedialog.asksaveasfilename(
            parent=self.top,
            defaultextension=".csv",
            filetypes=[("CSV 文件", "*.csv")],
            title="保存导出文件",
        )
        if not filepath:
            return

        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["类型", "名称", "所属项目", "截止日期", "完成状态"])
            writer.writeheader()
            writer.writerows(rows)

        messagebox.showinfo("导出完成", f"已导出 {len(rows)} 条记录到:\n{filepath}", parent=self.top)
        self.top.destroy()
