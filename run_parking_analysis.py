#!/usr/bin/env python3
"""
주차장 점유 현황 분석 실행 스크립트
YOLO 차량 인식 → ROI 비교 → 백엔드 전송 (IoU 기반)
"""

import os
import sys
import subprocess
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('run_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def activate_environment():
    """가상환경 활성화"""
    try:
        # 가상환경 활성화 명령어
        activate_cmd = "source yolo_env/bin/activate"
        logger.info("가상환경 활성화 중...")
        
        # 현재 환경에서 Python 경로 확인
        python_path = subprocess.check_output(["which", "python3"], text=True).strip()
        logger.info(f"Python 경로: {python_path}")
        
        return True
    except Exception as e:
        logger.error(f"가상환경 활성화 실패: {e}")
        return False

def run_yolo_detection():
    """YOLO 차량 인식 실행 (iou 0.2)"""
    try:
        logger.info("YOLO 차량 인식 시작 (IoU 기반)...")
        
        # YOLO 인식 명령어 (iou 0.2로 변경)
        cmd = [
            "python3", "detect.py",
            "--weights", "best_macos.pt",
            "--source", "frame_30min.jpg",
            "--conf", "0.0399",
            "--iou", "0.2",  # 0.0에서 0.2로 변경
            "--save-txt",
            "--project", "runs/detect",
            "--name", "occupancy_analysis"
        ]
        
        logger.info(f"실행 명령어: {' '.join(cmd)}")
        
        # 명령어 실행
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("YOLO 차량 인식 완료")
            return True
        else:
            logger.error(f"YOLO 인식 실패: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"YOLO 인식 실행 중 오류: {e}")
        return False

def run_occupancy_analysis():
    """점유 현황 분석 실행 (IoU 기반)"""
    try:
        logger.info("점유 현황 분석 시작 (IoU 기반)...")
        
        # 점유 현황 분석 실행
        cmd = ["python3", "parking_occupancy_analyzer.py"]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("점유 현황 분석 완료")
            return True
        else:
            logger.error(f"점유 현황 분석 실패: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"점유 현황 분석 실행 중 오류: {e}")
        return False

def main():
    """메인 실행 함수"""
    logger.info("=== 주차장 점유 현황 분석 시스템 시작 (IoU 기반) ===")
    
    # 1. 가상환경 활성화 확인
    if not activate_environment():
        logger.error("가상환경 활성화 실패")
        return
    
    # 2. 필요한 파일 확인
    required_files = [
        "best_macos.pt",
        "frame_30min.jpg",
        "roi_full_rect_coords.json",
        "detect.py"
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            logger.error(f"필요한 파일이 없습니다: {file_path}")
            return
    
    logger.info("모든 필요한 파일 확인 완료")
    
    # 3. YOLO 차량 인식 실행 (iou 0.2)
    if not run_yolo_detection():
        logger.error("YOLO 인식 실패")
        return
    
    # 4. 점유 현황 분석 실행 (IoU 기반)
    if not run_occupancy_analysis():
        logger.error("점유 현황 분석 실패")
        return
    
    logger.info("=== 주차장 점유 현황 분석 완료 (IoU 기반) ===")

if __name__ == "__main__":
    main() 