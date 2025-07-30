"""
Flask Web应用模块
"""

import os
import time
import logging
from flask import Flask, render_template, Response, jsonify, request
from werkzeug.utils import secure_filename
import cv2

from .detector import YOLODetector
from .config import Config

logger = logging.getLogger(__name__)

def create_app(config: Config = None) -> Flask:
    """创建Flask应用"""
    if config is None:
        config = Config.from_env()
    
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = config.max_content_length
    app.config['UPLOAD_FOLDER'] = config.upload_folder
    
    # 全局检测器实例
    detector = None
    
    def get_detector():
        """获取检测器实例"""
        nonlocal detector
        if detector is None:
            detector = YOLODetector(
                model_path=config.default_model_path,
                confidence_threshold=config.confidence_threshold
            )
            detector.initialize_camera(
                camera_index=config.camera_index,
                width=config.camera_width,
                height=config.camera_height
            )
        return detector
    
    def generate_frames():
        """生成视频帧"""
        detector = get_detector()
        
        while True:
            try:
                frame = detector.get_frame()
                if frame is None:
                    # 创建错误帧
                    frame = create_error_frame("无法获取摄像头画面")
                
                # 编码帧
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                if not ret:
                    continue
                
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
                # 控制帧率
                time.sleep(0.1)  # 约10 FPS
                
            except Exception as e:
                logger.error(f"生成帧时出错: {e}")
                error_frame = create_error_frame(f"错误: {str(e)}")
                ret, buffer = cv2.imencode('.jpg', error_frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                time.sleep(1)
    
    def create_error_frame(message: str):
        """创建错误信息帧"""
        import numpy as np
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(frame, message, (50, 240), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 255), 2, cv2.LINE_AA)
        return frame
    
    def allowed_file(filename):
        """检查文件扩展名是否允许"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in config.allowed_extensions
    
    @app.route('/')
    def index():
        """主页"""
        return render_template('index.html')
    
    @app.route('/video_feed')
    def video_feed():
        """视频流端点"""
        return Response(generate_frames(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    
    @app.route('/api/status')
    def get_status():
        """获取检测状态API"""
        try:
            detector = get_detector()
            status = detector.get_detection_status()
            
            return jsonify({
                'status': 'success',
                'message': '正常运行',
                **status
            })
        except Exception as e:
            logger.error(f"获取状态时出错: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e),
                'detection_count': 0,
                'detections': [],
                'timestamp': time.time()
            })
    
    @app.route('/api/config', methods=['GET', 'POST'])
    def manage_config():
        """配置管理API"""
        if request.method == 'GET':
            # 获取当前配置
            detector = get_detector()
            return jsonify({
                'model_path': detector.model_path,
                'confidence_threshold': detector.confidence_threshold,
                'camera_index': config.camera_index,
                'camera_width': config.camera_width,
                'camera_height': config.camera_height
            })
        
        elif request.method == 'POST':
            # 更新配置
            data = request.get_json()
            detector = get_detector()
            
            if 'confidence_threshold' in data:
                threshold = float(data['confidence_threshold'])
                if 0 <= threshold <= 1:
                    detector.confidence_threshold = threshold
                else:
                    return jsonify({'status': 'error', 'message': '置信度阈值必须在0-1之间'})
            
            return jsonify({'status': 'success', 'message': '配置更新成功'})
    
    @app.route('/api/model', methods=['POST'])
    def upload_model():
        """上传并更换模型API"""
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': '没有文件被上传'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': '没有选择文件'})
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # 尝试更换模型
            detector = get_detector()
            if detector.change_model(filepath):
                return jsonify({
                    'status': 'success', 
                    'message': f'模型更换成功: {filename}',
                    'model_path': filepath
                })
            else:
                # 删除无效文件
                os.remove(filepath)
                return jsonify({'status': 'error', 'message': '模型文件无效'})
        
        return jsonify({'status': 'error', 'message': '不支持的文件格式'})
    
    @app.route('/api/restart')
    def restart_detector():
        """重启检测器API"""
        nonlocal detector
        try:
            if detector:
                detector.cleanup()
            detector = None
            
            return jsonify({
                'status': 'success',
                'message': '检测器重启成功'
            })
        except Exception as e:
            logger.error(f"重启检测器时出错: {e}")
            return jsonify({
                'status': 'error',
                'message': f'重启失败: {str(e)}'
            })
    
    @app.errorhandler(404)
    def not_found(error):
        """404错误处理"""
        return jsonify({'status': 'error', 'message': '页面未找到'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500错误处理"""
        return jsonify({'status': 'error', 'message': '服务器内部错误'}), 500
    
    return app
