"""
YOLOWeb - 通用YOLO检测Web服务

一个基于Flask和YOLO的通用目标检测Web服务，支持：
- 实时摄像头检测
- 动态模型替换
- Web界面展示
- RESTful API接口
"""

__version__ = "1.0.0"
__author__ = "YOLOWeb Team"
__email__ = "your-email@example.com"

from .detector import YOLODetector
from .app import create_app
from .config import Config

__all__ = [
    'YOLODetector',
    'create_app', 
    'Config',
]
