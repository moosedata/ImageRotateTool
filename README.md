# ImageRotateTool

图像绕轴透视变换工具（Windows 免安装 exe）。

## 功能

- 打开 BMP/PNG/JPG/TIFF 图像
- 绕 X / Y / Z 轴旋转，支持角度输入
- 绕指定支点旋转（鼠标点击或手动输入坐标）
- XY 平移偏移
- 焦距 f 可调（控制透视强度）
- 变换累加：每次执行在当前结果上继续变换
- 一键重置原图
- 保存结果为 BMP/PNG/JPG

## 使用

双击 `ImageRotateTool.exe` 即可运行，无需安装 Python。

## 编译

```bash
pip install opencv-python numpy pillow pyinstaller
pyinstaller --onefile --windowed --name ImageRotateTool --collect-submodules cv2 rotate_tool.py
```
