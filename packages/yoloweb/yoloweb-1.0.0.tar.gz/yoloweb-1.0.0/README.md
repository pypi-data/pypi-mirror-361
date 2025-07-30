# YOLOWeb - 通用YOLO检测Web服务

一个基于Flask和YOLO的通用目标检测Web服务，支持实时摄像头检测、动态模型替换和Web界面展示。

## ✨ 功能特点

- 🎯 **通用YOLO检测**: 支持所有YOLO模型格式 (.pt, .onnx, .engine)
- 📹 **实时摄像头检测**: 高性能实时视频流检测
- 🔄 **动态模型替换**: 无需重启即可更换检测模型
- 🌐 **Web界面**: 现代化的Web管理界面
- 🚀 **RESTful API**: 完整的API接口支持
- 📊 **检测结果展示**: 实时显示检测框和置信度
- ⚙️ **灵活配置**: 支持多种配置方式

## 🚀 快速开始

### 安装

```bash
pip install yoloweb
```

### 基本使用

```bash
# 启动Web服务 (默认使用yolov8n.pt模型)
yoloweb --mode web

# 指定自定义模型
yoloweb --mode web --model your_model.pt --confidence 0.6

# 自定义服务器配置
yoloweb --mode web --host 0.0.0.0 --port 8080 --camera 0
```

### 从源码安装

```bash
git clone https://github.com/yourusername/yoloweb.git
cd yoloweb
pip install -e .
```

## 📖 使用说明

### 命令行参数

```bash
yoloweb --help
```

| 参数             | 说明             | 默认值         |
| ---------------- | ---------------- | -------------- |
| `--mode`       | 运行模式         | `web`        |
| `--host`       | 服务器主机地址   | `0.0.0.0`    |
| `--port`       | 服务器端口       | `5000`       |
| `--model`      | YOLO模型文件路径 | `yolov8n.pt` |
| `--confidence` | 检测置信度阈值   | `0.5`        |
| `--camera`     | 摄像头索引       | `0`          |
| `--width`      | 摄像头画面宽度   | `1280`       |
| `--height`     | 摄像头画面高度   | `720`        |
| `--debug`      | 启用调试模式     | `False`      |

### Web界面功能

启动服务后，访问 `http://localhost:5000` 即可使用Web界面：

- **实时检测画面**: 查看摄像头实时检测结果
- **检测状态监控**: 实时显示检测统计信息
- **模型管理**: 上传和切换YOLO模型文件
- **参数调整**: 动态调整置信度阈值等参数
- **系统控制**: 重启检测器等系统操作

## 🔧 API接口

### 获取检测状态

```bash
GET /api/status
```

响应示例：

```json
{
  "status": "success",
  "model_path": "yolov8n.pt",
  "confidence_threshold": 0.5,
  "detection_count": 3,
  "detections": [
    {
      "bbox": [100, 150, 300, 400],
      "confidence": 0.85,
      "class_id": 0,
      "class_name": "person"
    }
  ],
  "timestamp": 1640995200.0
}
```

### 上传模型

```bash
POST /api/model
Content-Type: multipart/form-data

# 上传模型文件
curl -X POST -F "file=@your_model.pt" http://localhost:5000/api/model
```

### 更新配置

```bash
POST /api/config
Content-Type: application/json

{
  "confidence_threshold": 0.6
}
```

### 重启检测器

```bash
GET /api/restart
```

## 💻 编程接口

### 基本使用

```python
from yoloweb import YOLODetector, create_app, Config

# 创建检测器
detector = YOLODetector(model_path="yolov8n.pt", confidence_threshold=0.5)

# 初始化摄像头
detector.initialize_camera(camera_index=0, width=1280, height=720)

# 获取检测结果
frame = detector.get_frame()  # 返回标注后的图像
status = detector.get_detection_status()  # 返回检测状态

# 动态更换模型
success = detector.change_model("new_model.pt")
```

### 创建Web应用

```python
from yoloweb import create_app, Config

# 创建配置
config = Config(
    default_model_path="yolov8n.pt",
    confidence_threshold=0.5,
    flask_host="0.0.0.0",
    flask_port=5000
)

# 创建Flask应用
app = create_app(config)
app.run()
```

## 🛠️ 环境变量配置

```bash
# 模型配置
export YOLO_MODEL_PATH="your_model.pt"
export CONFIDENCE_THRESHOLD=0.5

# 摄像头配置
export CAMERA_INDEX=0
export CAMERA_WIDTH=1280
export CAMERA_HEIGHT=720

# 服务器配置
export FLASK_HOST="0.0.0.0"
export FLASK_PORT=5000
export FLASK_DEBUG=false
```

## 📋 系统要求

- Python 3.8+
- OpenCV 4.0+
- PyTorch 2.0+
- 摄像头设备 (可选)

## 🔍 支持的模型格式

- **PyTorch模型**: `.pt` 格式
- **ONNX模型**: `.onnx` 格式
- **TensorRT模型**: `.engine` 格式

## 🐳 Docker部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

EXPOSE 5000
CMD ["yoloweb", "--mode", "web", "--host", "0.0.0.0"]
```

```bash
# 构建和运行
docker build -t yoloweb .
docker run -p 5000:5000 --device=/dev/video0 yoloweb
```

## 📄 许可证

MIT License - 查看 [LICENSE](LICENSE) 文件了解详情。
