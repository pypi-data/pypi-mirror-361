#!/usr/bin/env python3
"""
YOLOWeb主启动模块
"""

import os
import sys
import argparse
import logging
from .app import create_app
from .config import Config

# 设置环境变量以避免OpenMP冲突
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

def setup_logging(debug: bool = False):
    """设置日志"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('yoloweb.log')
        ]
    )

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="YOLOWeb - 通用YOLO检测Web服务")
    parser.add_argument("--mode", choices=["web"], default="web",
                       help="运行模式 (目前只支持web模式)")
    parser.add_argument("--host", default="0.0.0.0",
                       help="Flask服务器主机地址")
    parser.add_argument("--port", type=int, default=5000,
                       help="Flask服务器端口")
    parser.add_argument("--model", default="yolov8n.pt",
                       help="YOLO模型文件路径")
    parser.add_argument("--confidence", type=float, default=0.5,
                       help="检测置信度阈值 (0-1)")
    parser.add_argument("--camera", type=int, default=0,
                       help="摄像头索引")
    parser.add_argument("--width", type=int, default=1280,
                       help="摄像头画面宽度")
    parser.add_argument("--height", type=int, default=720,
                       help="摄像头画面高度")
    parser.add_argument("--debug", action="store_true",
                       help="启用调试模式")
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 50)
    logger.info("YOLOWeb - 通用YOLO检测Web服务启动")
    logger.info("=" * 50)
    
    try:
        # 创建配置
        config = Config(
            default_model_path=args.model,
            confidence_threshold=args.confidence,
            camera_index=args.camera,
            camera_width=args.width,
            camera_height=args.height,
            flask_host=args.host,
            flask_port=args.port,
            flask_debug=args.debug
        )
        
        # 验证配置
        config.validate()
        logger.info("配置验证通过")
        
        # 检查模型文件
        if not os.path.exists(config.default_model_path):
            logger.warning(f"⚠️ 模型文件不存在: {config.default_model_path}")
            logger.info("将在首次检测时自动下载默认模型")
        
        # 创建Flask应用
        app = create_app(config)
        logger.info("Flask应用创建成功")
        
        # 启动Web服务器
        logger.info("Web服务器启动中...")
        logger.info(f"访问地址: http://{config.flask_host}:{config.flask_port}")
        logger.info(f"当前模型: {config.default_model_path}")
        logger.info(f"置信度阈值: {config.confidence_threshold}")
        logger.info(f"摄像头: {config.camera_index} ({config.camera_width}x{config.camera_height})")
        
        app.run(
            host=config.flask_host,
            port=config.flask_port,
            debug=config.flask_debug,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("用户中断，正在退出...")
        return 0
    except Exception as e:
        logger.error(f"启动失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
