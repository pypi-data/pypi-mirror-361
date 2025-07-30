"""
通用YOLO检测器模块
"""

import os
import time
import threading
import logging
from typing import Optional, Dict, List, Tuple
import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv

logger = logging.getLogger(__name__)

class YOLODetector:
    """通用YOLO检测器"""
    
    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.5):
        """
        初始化YOLO检测器
        
        Args:
            model_path: YOLO模型文件路径
            confidence_threshold: 置信度阈值
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.cap = None
        self.detection_lock = threading.Lock()
        self.last_detections = []
        self.detection_count = 0
        
        # 初始化supervision注释器
        self.box_annotator = sv.BoxAnnotator()
        self.label_annotator = sv.LabelAnnotator()
        
        # 加载模型
        self._load_model()
        
    def _load_model(self):
        """加载YOLO模型"""
        try:
            logger.info(f"正在加载YOLO模型: {self.model_path}")
            self.model = YOLO(self.model_path)
            logger.info("YOLO模型加载成功")
        except Exception as e:
            logger.error(f"YOLO模型加载失败: {e}")
            raise RuntimeError(f"模型加载失败: {e}")
    
    def change_model(self, new_model_path: str) -> bool:
        """
        动态更换模型
        
        Args:
            new_model_path: 新模型文件路径
            
        Returns:
            bool: 是否成功更换模型
        """
        try:
            if not os.path.exists(new_model_path):
                logger.error(f"模型文件不存在: {new_model_path}")
                return False
                
            logger.info(f"正在更换模型: {new_model_path}")
            new_model = YOLO(new_model_path)
            
            with self.detection_lock:
                self.model = new_model
                self.model_path = new_model_path
                
            logger.info("模型更换成功")
            return True

        except Exception as e:
            logger.error(f"模型更换失败: {e}")
            return False
    
    def initialize_camera(self, camera_index: int = 0, width: int = 1280, height: int = 720):
        """
        初始化摄像头
        
        Args:
            camera_index: 摄像头索引
            width: 画面宽度
            height: 画面高度
        """
        try:
            self.cap = cv2.VideoCapture(camera_index)
            if not self.cap.isOpened():
                raise RuntimeError(f"无法打开摄像头 {camera_index}")
            
            # 设置摄像头参数
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            logger.info(f"摄像头初始化成功 (索引: {camera_index}, 分辨率: {width}x{height})")

        except Exception as e:
            logger.error(f"摄像头初始化失败: {e}")
            raise
    
    def detect_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, List[Dict]]:
        """
        对单帧进行检测
        
        Args:
            frame: 输入图像帧
            
        Returns:
            Tuple[np.ndarray, List[Dict]]: (标注后的图像, 检测结果列表)
        """
        if self.model is None:
            return frame, []
        
        try:
            with self.detection_lock:
                # 使用YOLO进行检测
                results = self.model(frame, conf=self.confidence_threshold, verbose=False)[0]
                
                # 使用supervision转换检测结果
                detections = sv.Detections.from_ultralytics(results)
                
                # 绘制检测框和标签
                annotated_frame = self.box_annotator.annotate(
                    scene=frame.copy(), detections=detections
                )
                annotated_frame = self.label_annotator.annotate(
                    scene=annotated_frame, detections=detections
                )
                
                # 转换检测结果为字典格式
                detection_list = []
                if len(detections) > 0:
                    for i in range(len(detections)):
                        bbox = detections.xyxy[i]
                        confidence = detections.confidence[i] if detections.confidence is not None else 0.0
                        class_id = detections.class_id[i] if detections.class_id is not None else 0
                        
                        # 获取类别名称
                        class_name = self.model.names.get(class_id, f"Class_{class_id}")
                        
                        detection_list.append({
                            'bbox': [int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])],
                            'confidence': float(confidence),
                            'class_id': int(class_id),
                            'class_name': class_name
                        })
                
                # 更新检测结果
                self.last_detections = detection_list
                self.detection_count = len(detection_list)
                
                return annotated_frame, detection_list
                
        except Exception as e:
            logger.error(f"检测过程中出错: {e}")
            return frame, []
    
    def get_frame(self) -> Optional[np.ndarray]:
        """
        从摄像头获取处理后的帧
        
        Returns:
            Optional[np.ndarray]: 处理后的图像帧，如果失败返回None
        """
        if self.cap is None:
            logger.warning("摄像头未初始化")
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            logger.warning("无法从摄像头读取画面")
            return None
        
        # 进行检测并返回标注后的帧
        annotated_frame, _ = self.detect_frame(frame)
        return annotated_frame
    
    def get_detection_status(self) -> Dict:
        """
        获取当前检测状态
        
        Returns:
            Dict: 检测状态信息
        """
        return {
            'model_path': self.model_path,
            'confidence_threshold': self.confidence_threshold,
            'detection_count': self.detection_count,
            'detections': self.last_detections,
            'timestamp': time.time()
        }
    
    def cleanup(self):
        """清理资源"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        logger.info("检测器资源清理完成")
