import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
import math
import os
from PIL import Image, ImageTk

class RotateTool:
    def __init__(self, root):
        self.root = root
        self.root.title("图像绕轴变换工具")
        self.root.geometry("900x750")

        self.img_orig = None    # 原始图
        self.img_work = None    # 当前工作图（累加变换后的）
        self.pivot = None

        # ---- 第一行 ----
        top = tk.Frame(root)
        top.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(top, text="打开图片", command=self.open_img).pack(side=tk.LEFT, padx=2)
        tk.Button(top, text="保存结果", command=self.save_img).pack(side=tk.LEFT, padx=2)
        tk.Button(top, text="重置原图", command=self.reset_img, bg="#c66", fg="white").pack(side=tk.LEFT, padx=2)

        tk.Label(top, text="  轴:").pack(side=tk.LEFT)
        self.axis = tk.StringVar(value="X")
        for ax in ["X", "Y", "Z"]:
            tk.Radiobutton(top, text=ax, variable=self.axis, value=ax).pack(side=tk.LEFT)

        tk.Label(top, text="  角度:").pack(side=tk.LEFT)
        self.angle_entry = tk.Entry(top, width=8)
        self.angle_entry.insert(0, "19.399")
        self.angle_entry.pack(side=tk.LEFT)

        tk.Label(top, text="  f:").pack(side=tk.LEFT)
        self.f_entry = tk.Entry(top, width=8)
        self.f_entry.insert(0, "1280")
        self.f_entry.pack(side=tk.LEFT)

        # ---- 第二行: 平移 ----
        row2 = tk.Frame(root)
        row2.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(row2, text="平移TX:").pack(side=tk.LEFT)
        self.tx_entry = tk.Entry(row2, width=8)
        self.tx_entry.insert(0, "0")
        self.tx_entry.pack(side=tk.LEFT)
        tk.Label(row2, text="TY:").pack(side=tk.LEFT, padx=(5,0))
        self.ty_entry = tk.Entry(row2, width=8)
        self.ty_entry.insert(0, "0")
        self.ty_entry.pack(side=tk.LEFT)

        # ---- 第三行: 支点 ----
        row3 = tk.Frame(root)
        row3.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(row3, text="支点X:").pack(side=tk.LEFT)
        self.px_entry = tk.Entry(row3, width=8)
        self.px_entry.pack(side=tk.LEFT)
        tk.Label(row3, text="Y:").pack(side=tk.LEFT, padx=(5,0))
        self.py_entry = tk.Entry(row3, width=8)
        self.py_entry.pack(side=tk.LEFT)
        tk.Button(row3, text="应用支点", command=self.set_pivot_from_entry).pack(side=tk.LEFT, padx=5)
        self.pivot_label = tk.Label(row3, text="未设置", fg="gray")
        self.pivot_label.pack(side=tk.LEFT, padx=10)
        self.size_label = tk.Label(row3, text="")
        self.size_label.pack(side=tk.RIGHT)

        tk.Button(top, text="执行变换", command=self.do_transform,
                  bg="#4a9", fg="white", font=("", 11, "bold")).pack(side=tk.LEFT, padx=10)

        # ---- 画布 ----
        self.canvas = tk.Canvas(root, bg="#333", cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Configure>", lambda e: self.redraw())

    def open_img(self):
        path = filedialog.askopenfilename(
            filetypes=[("BMP/PNG/JPG", "*.bmp *.png *.jpg *.jpeg *.tif *.tiff"),
                       ("所有文件", "*.*")])
        if not path:
            return
        self.img_orig = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if self.img_orig is None:
            messagebox.showerror("错误", "无法读取图片")
            return
        self.reset_img()

    def reset_img(self):
        if self.img_orig is None:
            return
        self.img_work = self.img_orig.copy()
        h, w = self.img_orig.shape[:2]
        self.size_label.config(text=f"尺寸: {w}x{h}")
        self.pivot = (w/2, h/2)
        self.px_entry.delete(0, tk.END); self.px_entry.insert(0, f"{w/2:.1f}")
        self.py_entry.delete(0, tk.END); self.py_entry.insert(0, f"{h/2:.1f}")
        self.pivot_label.config(text=f"({w/2:.1f}, {h/2:.1f})")
        self.redraw()

    def set_pivot_from_entry(self):
        try:
            px, py = float(self.px_entry.get()), float(self.py_entry.get())
        except ValueError:
            messagebox.showwarning("提示", "支点坐标必须是数字"); return
        self.pivot = (px, py)
        self.pivot_label.config(text=f"({px:.1f}, {py:.1f})")
        self.redraw()

    def on_click(self, event):
        if self.img_work is None: return
        h, w = self.img_work.shape[:2]
        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        scale = min(cw/w, ch/h, 1.0)
        ox = (cw - w*scale)/2
        oy = (ch - h*scale)/2
        px = (event.x - ox)/scale
        py = (event.y - oy)/scale
        if 0 <= px < w and 0 <= py < h:
            self.pivot = (px, py)
            self.px_entry.delete(0, tk.END); self.px_entry.insert(0, f"{px:.1f}")
            self.py_entry.delete(0, tk.END); self.py_entry.insert(0, f"{py:.1f}")
            self.pivot_label.config(text=f"({px:.1f}, {py:.1f})")
            self.redraw()

    def redraw(self):
        self.canvas.delete("all")
        if self.img_work is None:
            self.canvas.create_text(400, 300, text="请打开图片", fill="gray", font=("", 20))
            return
        disp = self.img_work
        h, w = disp.shape[:2]
        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        scale = min(cw/w, ch/h, 1.0)
        nw, nh = int(w*scale), int(h*scale)
        ox = (cw - nw)//2; oy = (ch - nh)//2
        rgb = cv2.cvtColor(cv2.resize(disp, (nw, nh)), cv2.COLOR_BGR2RGB)
        self.tk_img = ImageTk.PhotoImage(Image.fromarray(rgb))
        self.canvas.create_image(ox, oy, anchor=tk.NW, image=self.tk_img)
        if self.pivot:
            px = ox + self.pivot[0]*scale
            py = oy + self.pivot[1]*scale
            self.canvas.create_oval(px-5,py-5,px+5,py+5, outline="red", width=2)
            self.canvas.create_line(px-10,py,px+10,py, fill="red")
            self.canvas.create_line(px,py-10,px,py+10, fill="red")

    def do_transform(self):
        if self.img_work is None:
            messagebox.showwarning("提示", "请先打开图片"); return
        h, w = self.img_work.shape[:2]
        cx0, cy0 = self.pivot
        try:
            angle = float(self.angle_entry.get())
            f = float(self.f_entry.get())
            tx = float(self.tx_entry.get())
            ty = float(self.ty_entry.get())
        except ValueError:
            messagebox.showerror("错误", "参数必须是数字"); return

        th = math.radians(angle)
        ct, st = math.cos(th), math.sin(th)
        axis = self.axis.get()

        src = np.float32([[0,0],[w,0],[w,h],[0,h]])
        dst = np.zeros_like(src)
        for i, (u, v) in enumerate(src):
            X = u - cx0; Y = v - cy0
            if axis == "Z":
                x2 = cx0 + X*ct - Y*st
                y2 = cy0 + X*st + Y*ct
            elif axis == "X":
                Zp = f + Y*st
                x2 = cx0 + f*X/Zp
                y2 = cy0 + f*Y*ct/Zp
            else:  # Y
                Zp = f + X*st
                x2 = cx0 + f*X*ct/Zp
                y2 = cy0 + f*Y/Zp
            dst[i] = [x2 + tx, y2 + ty]   # 平移叠加

        M = cv2.getPerspectiveTransform(src, dst)
        bg = int(np.median(self.img_work[5:20, 5:20]))
        # 在当前工作图上继续变换（累加）
        self.img_work = cv2.warpPerspective(self.img_work, M, (w, h),
                                            flags=cv2.INTER_LINEAR,
                                            borderMode=cv2.BORDER_CONSTANT,
                                            borderValue=(bg, bg, bg))
        self.redraw()

    def save_img(self):
        if self.img_work is None:
            messagebox.showwarning("提示", "还没有图片"); return
        path = filedialog.asksaveasfilename(defaultextension=".bmp",
            filetypes=[("BMP","*.bmp"),("PNG","*.png"),("JPG","*.jpg")])
        if not path: return
        ext = os.path.splitext(path)[1]
        ok, buf = cv2.imencode(ext, self.img_work)
        buf.tofile(path)
        messagebox.showinfo("完成", f"已保存:\n{path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RotateTool(root)
    root.mainloop()
