#!/usr/bin/env python3
"""
detect.py의 PyTorch 2.7 호환성 문제 해결 패치
"""

import os
import sys

def patch_detect_py():
    """detect.py 파일을 패치하여 PyTorch 2.7 호환성 문제 해결"""
    try:
        # detect.py 파일 읽기
        with open('detect.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 이미 패치되었는지 확인
        if 'weights_only=False' in content:
            print("✅ detect.py는 이미 패치되어 있습니다.")
            return True
        
        # 패치 적용
        old_line = 'ckpt = torch.load(attempt_download(w), map_location="cpu", weights_only=False)  # load'
        new_line = 'ckpt = torch.load(attempt_download(w), map_location="cpu", weights_only=False, pickle_module=torch._utils._rebuild_tensor_v2)  # load'
        
        if old_line in content:
            content = content.replace(old_line, new_line)
            
            # 파일 백업
            with open('detect.py.backup', 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 패치된 파일 저장
            with open('detect.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ detect.py 패치 완료")
            return True
        else:
            print("❌ 패치할 라인을 찾을 수 없습니다.")
            return False
            
    except Exception as e:
        print(f"❌ detect.py 패치 실패: {e}")
        return False

def create_simple_detect():
    """간단한 detect.py 대체 버전 생성"""
    try:
        simple_detect_content = '''#!/usr/bin/env python3
"""
간단한 YOLO detection 스크립트 (PyTorch 2.7 호환)
"""

import torch
import cv2
import numpy as np
import os
import sys
from pathlib import Path

def load_model(weights_path):
    """모델 로드 (PyTorch 2.7 호환)"""
    try:
        # 방법 1: weights_only=False
        model = torch.load(weights_path, map_location='cpu', weights_only=False)
        print(f"✅ 모델 로드 성공: {weights_path}")
        return model
    except Exception as e:
        print(f"❌ 모델 로드 실패: {e}")
        return None

def detect_objects(model, image_path, conf_thres=0.25, iou_thres=0.45):
    """객체 감지"""
    try:
        # 이미지 로드
        img = cv2.imread(image_path)
        if img is None:
            print(f"❌ 이미지를 로드할 수 없습니다: {image_path}")
            return []
        
        # 전처리
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_tensor = torch.from_numpy(img_rgb).permute(2, 0, 1).float() / 255.0
        img_tensor = img_tensor.unsqueeze(0)
        
        # 추론
        with torch.no_grad():
            predictions = model(img_tensor)
        
        # 결과 처리
        detections = []
        for pred in predictions[0]:
            if pred[4] >= conf_thres:  # confidence threshold
                x1, y1, x2, y2, conf, cls = pred[:6]
                detections.append({
                    'bbox': [x1.item(), y1.item(), x2.item(), y2.item()],
                    'confidence': conf.item(),
                    'class_id': int(cls.item())
                })
        
        return detections
        
    except Exception as e:
        print(f"❌ 객체 감지 실패: {e}")
        return []

def save_results(detections, output_path):
    """결과를 YOLO 형식으로 저장"""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            for det in detections:
                # YOLO 형식: class x_center y_center width height confidence
                bbox = det['bbox']
                x_center = (bbox[0] + bbox[2]) / 2
                y_center = (bbox[1] + bbox[3]) / 2
                width = bbox[2] - bbox[0]
                height = bbox[3] - bbox[1]
                
                f.write(f"{det['class_id']} {x_center} {y_center} {width} {height} {det['confidence']}\\n")
        
        print(f"✅ 결과 저장: {output_path}")
        
    except Exception as e:
        print(f"❌ 결과 저장 실패: {e}")

def main():
    """메인 함수"""
    if len(sys.argv) < 3:
        print("사용법: python3 simple_detect.py <weights> <image>")
        return
    
    weights_path = sys.argv[1]
    image_path = sys.argv[2]
    
    # 모델 로드
    model = load_model(weights_path)
    if model is None:
        return
    
    # 객체 감지
    detections = detect_objects(model, image_path)
    
    # 결과 저장
    output_dir = "runs/detect/simple_detection"
    os.makedirs(output_dir, exist_ok=True)
    
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    output_path = os.path.join(output_dir, "labels", f"{image_name}.txt")
    
    save_results(detections, output_path)

if __name__ == "__main__":
    main()
'''
        
        with open('simple_detect.py', 'w', encoding='utf-8') as f:
            f.write(simple_detect_content)
        
        os.chmod('simple_detect.py', 0o755)
        print("✅ simple_detect.py 생성 완료")
        return True
        
    except Exception as e:
        print(f"❌ simple_detect.py 생성 실패: {e}")
        return False

if __name__ == "__main__":
    print("🔧 detect.py 패치 시작...")
    
    # 방법 1: 기존 detect.py 패치
    if patch_detect_py():
        print("✅ 패치 완료")
    else:
        # 방법 2: 간단한 대체 버전 생성
        print("🔄 간단한 대체 버전 생성...")
        if create_simple_detect():
            print("✅ 대체 버전 생성 완료")
        else:
            print("❌ 모든 방법 실패")
            sys.exit(1)
