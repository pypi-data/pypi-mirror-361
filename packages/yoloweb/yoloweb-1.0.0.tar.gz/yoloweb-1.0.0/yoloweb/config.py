"""
配置管理模块
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """应用配置类"""
    
    # 模型配置
    default_model_path: str = "yolov8n.pt"
    confidence_threshold: float = 0.5
    
    # 摄像头配置
    camera_index: int = 0
    camera_width: int = 1280
    camera_height: int = 720
    
    # Flask配置
    flask_host: str = "0.0.0.0"
    flask_port: int = 5000
    flask_debug: bool = False
    
    # 上传配置
    upload_folder: str = "uploads"
    max_content_length: int = 16 * 1024 * 1024  # 16MB
    allowed_extensions: set = None
    
    def __post_init__(self):
        if self.allowed_extensions is None:
            self.allowed_extensions = {'pt', 'onnx', 'engine'}
        
        # 创建上传目录
        os.makedirs(self.upload_folder, exist_ok=True)
    
    @classmethod
    def from_env(cls) -> 'Config':
        """从环境变量创建配置"""
        config = cls()
        
        # 从环境变量读取配置
        if os.getenv("YOLO_MODEL_PATH"):
            config.default_model_path = os.getenv("YOLO_MODEL_PATH")
        
        if os.getenv("CONFIDENCE_THRESHOLD"):
            config.confidence_threshold = float(os.getenv("CONFIDENCE_THRESHOLD"))
        
        if os.getenv("CAMERA_INDEX"):
            config.camera_index = int(os.getenv("CAMERA_INDEX"))
        
        if os.getenv("CAMERA_WIDTH"):
            config.camera_width = int(os.getenv("CAMERA_WIDTH"))
        
        if os.getenv("CAMERA_HEIGHT"):
            config.camera_height = int(os.getenv("CAMERA_HEIGHT"))
        
        if os.getenv("FLASK_HOST"):
            config.flask_host = os.getenv("FLASK_HOST")
        
        if os.getenv("FLASK_PORT"):
            config.flask_port = int(os.getenv("FLASK_PORT"))
        
        if os.getenv("FLASK_DEBUG"):
            config.flask_debug = os.getenv("FLASK_DEBUG").lower() == "true"
        
        return config
    
    def validate(self) -> bool:
        """验证配置"""
        errors = []
        
        # 检查置信度阈值
        if not 0 <= self.confidence_threshold <= 1:
            errors.append("置信度阈值必须在0-1之间")
        
        # 检查摄像头索引
        if self.camera_index < 0:
            errors.append("摄像头索引不能为负数")
        
        # 检查端口
        if not 1 <= self.flask_port <= 65535:
            errors.append("Flask端口必须在1-65535之间")
        
        # 检查分辨率
        if self.camera_width <= 0 or self.camera_height <= 0:
            errors.append("摄像头分辨率必须大于0")
        
        if errors:
            raise ValueError("配置验证失败:\n" + "\n".join(errors))
        
        return True
