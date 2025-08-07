#!/usr/bin/env python3
"""
주차장 점유 현황 분석 및 백엔드 전송 시스템
YOLO 차량 인식 결과를 ROI 좌표와 비교하여 주차장 점유율 계산 (IoU 기반)
"""

import cv2
import json
import time
import requests
import numpy as np
from datetime import datetime
import torch
from models.experimental import attempt_load
from utils.general import non_max_suppression, scale_boxes
import logging
from typing import List, Dict, Tuple, Optional
import os
import subprocess
from shapely.geometry import box, Polygon

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('parking_occupancy.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ParkingOccupancyAnalyzer:
    def __init__(self, 
                 roi_path: str = "roi_manual_coords.json",
                 model_path: str = "best_linux.pt",  # Linux용 모델로 변경
                 backend_url: str = "http://localhost:8080",
                 image_path: str = "frame_30min.jpg"):
        """
        주차장 점유 현황 분석기 초기화
        
        Args:
            roi_path: ROI 좌표 JSON 파일 경로
            model_path: YOLO 모델 파일 경로
            backend_url: 백엔드 서버 URL
            image_path: 분석할 이미지 파일 경로
        """
        self.roi_path = roi_path
        self.model_path = model_path
        self.backend_url = backend_url
        self.image_path = image_path
        
        # 초기화
        self.roi_data = self.load_roi_data()
        self.model = self.load_yolo_model()
        
        logger.info(f"주차장 점유 현황 분석기 초기화 완료")
        
    def load_roi_data(self) -> Dict:
        """ROI 좌표 데이터 로드"""
        try:
            with open(self.roi_path, 'r', encoding='utf-8') as f:
                roi_data = json.load(f)
            logger.info(f"ROI 데이터 로드 완료 - {len(roi_data)}개 이미지의 슬롯 정보")
            return roi_data
        except Exception as e:
            logger.error(f"ROI 데이터 로드 실패: {e}")
            return {}
    
    def load_yolo_model(self):
        """YOLO 모델 로드"""
        try:
            # Linux 환경에서는 모델 로드를 건너뛰고 detect.py에서 처리
            logger.info("Linux 환경: YOLO 모델은 detect.py에서 로드됩니다.")
            return None
        except Exception as e:
            logger.error(f"YOLO 모델 로드 실패: {e}")
            return None
    
    def run_yolo_detection(self) -> List[Dict]:
        """YOLO 차량 인식 실행 (iou 0.2로 변경)"""
        try:
            # YOLO 인식 명령어 실행 (iou 0.2로 변경)
            cmd = [
                "python3", "detect.py",
                "--weights", "best_linux.pt",  # Linux용 모델로 변경
                "--source", self.image_path,
                "--conf", "0.0399",
                "--iou", "0.2",  # 0.0에서 0.2로 변경
                "--save-txt",
                "--project", "runs/detect",
                "--name", "occupancy_analysis"
            ]
            
            logger.info(f"YOLO 인식 실행: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"YOLO 인식 실패: {result.stderr}")
                return []
            
            # 인식 결과 파일 읽기
            txt_file = f"runs/detect/occupancy_analysis/labels/{os.path.splitext(os.path.basename(self.image_path))[0]}.txt"
            
            if not os.path.exists(txt_file):
                logger.warning(f"인식 결과 파일이 없습니다: {txt_file}")
                return []
            
            detections = []
            with open(txt_file, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        # YOLO 형식: class x_center y_center width height
                        class_id = int(parts[0])
                        x_center = float(parts[1])
                        y_center = float(parts[2])
                        width = float(parts[3])
                        height = float(parts[4])
                        confidence = float(parts[5]) if len(parts) > 5 else 1.0
                        
                        detections.append({
                            'class_id': class_id,
                            'x_center': x_center,
                            'y_center': y_center,
                            'width': width,
                            'height': height,
                            'confidence': confidence
                        })
            
            logger.info(f"차량 인식 완료: {len(detections)}개 객체 감지")
            return detections
            
        except Exception as e:
            logger.error(f"YOLO 인식 실행 중 오류: {e}")
            return []
    
    def normalize_coordinates(self, detections: List[Dict], image_shape: Tuple[int, int]) -> List[Dict]:
        """좌표를 픽셀 단위로 변환"""
        height, width = image_shape
        normalized_detections = []
        
        for det in detections:
            # YOLO 좌표를 픽셀 좌표로 변환
            x_center_px = int(det['x_center'] * width)
            y_center_px = int(det['y_center'] * height)
            w_px = int(det['width'] * width)
            h_px = int(det['height'] * height)
            
            # 바운딩 박스 좌표 계산
            x1 = x_center_px - w_px // 2
            y1 = y_center_px - h_px // 2
            x2 = x_center_px + w_px // 2
            y2 = y_center_px + h_px // 2
            
            normalized_detections.append({
                'class_id': det['class_id'],
                'confidence': det['confidence'],
                'bbox': [x1, y1, x2, y2],
                'center': [x_center_px, y_center_px]
            })
        
        return normalized_detections
    
    def calculate_iou(self, bbox: List[float], roi_coords: List[List[int]]) -> float:
        """IoU 계산 함수 (judge_occupancy.py 참고)"""
        try:
            bbox_poly = box(*bbox)
            roi_poly = Polygon(roi_coords)
            
            if not bbox_poly.intersects(roi_poly):
                return 0.0
            
            intersection_area = bbox_poly.intersection(roi_poly).area
            union_area = bbox_poly.union(roi_poly).area
            
            return intersection_area / union_area if union_area > 0 else 0.0
            
        except Exception as e:
            logger.warning(f"IoU 계산 중 오류: {e}")
            return 0.0
    
    def check_parking_slots_iou(self, detections: List[Dict]) -> List[Dict]:
        """IoU 기반 주차 슬롯별 점유 현황 확인 (judge_occupancy.py 참고)"""
        # 이미지 로드하여 크기 확인
        image = cv2.imread(self.image_path)
        if image is None:
            logger.error(f"이미지를 로드할 수 없습니다: {self.image_path}")
            return []
        
        height, width = image.shape[:2]
        normalized_detections = self.normalize_coordinates(detections, (height, width))
        
        # ROI 데이터에서 frame_30min.jpg의 슬롯 정보 사용
        image_key = "frame_30min.jpg"
        slots = self.roi_data.get(image_key, [])
        
        slot_status = []
        
        for slot in slots:
            slot_id = slot['slot_id']
            coords = slot['coords']
            
            # IoU 기반 점유 판단 (judge_occupancy.py 참고)
            max_iou = 0.0
            vehicle_count = 0
            
            for det in normalized_detections:
                # 차량 클래스 ID 확인 (0: car, 2: car, 3: motorcycle, 5: bus, 7: truck)
                if det['class_id'] in [0, 2, 3, 5, 7]:
                    iou = self.calculate_iou(det['bbox'], coords)
                    if iou > max_iou:
                        max_iou = iou
                    if iou >= 0.1:  # judge_occupancy.py와 동일한 임계값
                        vehicle_count += 1
            
            # IoU 임계값 0.17 이상이면 점유로 판단
            occupied = max_iou >= 0.17
            
            slot_status.append({
                'slot_id': slot_id,
                'occupied': occupied,
                'vehicle_count': vehicle_count,
                'max_iou': round(max_iou, 3),
                'coordinates': coords
            })
        
        return slot_status
    
    def calculate_occupancy_rate(self, slot_status: List[Dict]) -> Dict:
        """전체 점유율 계산"""
        total_slots = len(slot_status)
        occupied_slots = sum(1 for slot in slot_status if slot['occupied'])
        total_vehicles = sum(slot['vehicle_count'] for slot in slot_status)
        
        occupancy_rate = (occupied_slots / total_slots * 100) if total_slots > 0 else 0
        
        return {
            'total_slots': total_slots,
            'occupied_slots': occupied_slots,
            'total_vehicles': total_vehicles,
            'occupancy_rate': round(occupancy_rate, 1),
            'occupancy_ratio': f"{occupied_slots}/{total_slots}"
        }
    
    def send_to_backend(self, slot_status: List[Dict], occupancy_info: Dict, timestamp: datetime) -> bool:
        """백엔드 서버로 JSON 데이터 전송"""
        try:
            # 전송할 데이터 구성 (JSON 형식)
            payload = {
                'timestamp': timestamp.isoformat(),
                'parking_lot_id': 'sanggyeonggwan',  # 주차장 ID
                'occupancy_info': occupancy_info,
                'slot_details': [
                    {
                        'slot_id': slot['slot_id'],
                        'occupied': slot['occupied'],
                        'vehicle_count': slot['vehicle_count'],
                        'max_iou': slot['max_iou']
                    }
                    for slot in slot_status
                ]
            }
            
            # 백엔드 API 엔드포인트
            url = f"{self.backend_url}/parking-lots/occupancy"
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer yolo_token'  # YOLO 서비스 토큰
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"백엔드 전송 성공: {occupancy_info['occupancy_ratio']} ({occupancy_info['occupancy_rate']}%)")
                return True
            else:
                logger.error(f"백엔드 전송 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"백엔드 전송 중 오류: {e}")
            return False
    
    def save_analysis_result(self, slot_status: List[Dict], occupancy_info: Dict, timestamp: datetime):
        """분석 결과를 JSON 파일로 저장"""
        result = {
            'timestamp': timestamp.isoformat(),
            'occupancy_info': occupancy_info,
            'slot_status': slot_status
        }
        
        # JSON 파일로 저장
        filename = f"occupancy_result_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"분석 결과 저장: {filename}")
    
    def run_analysis(self):
        """전체 분석 프로세스 실행"""
        logger.info("주차장 점유 현황 분석 시작 (IoU 기반)")
        
        # 1. YOLO 차량 인식 실행 (iou 0.2)
        detections = self.run_yolo_detection()
        if not detections:
            logger.error("차량 인식 실패")
            return
        
        # 2. IoU 기반 주차 슬롯 점유 현황 확인
        slot_status = self.check_parking_slots_iou(detections)
        if not slot_status:
            logger.error("주차 슬롯 분석 실패")
            return
        
        # 3. 점유율 계산
        occupancy_info = self.calculate_occupancy_rate(slot_status)
        
        # 4. 현재 시간
        timestamp = datetime.now()
        
        # 5. 결과 출력
        logger.info(f"분석 완료 (IoU 기반):")
        logger.info(f"  - 전체 슬롯: {occupancy_info['total_slots']}개")
        logger.info(f"  - 점유 슬롯: {occupancy_info['occupied_slots']}개")
        logger.info(f"  - 전체 차량: {occupancy_info['total_vehicles']}대")
        logger.info(f"  - 점유율: {occupancy_info['occupancy_ratio']} ({occupancy_info['occupancy_rate']}%)")
        
        # 6. 백엔드 전송 (JSON 형식)
        success = self.send_to_backend(slot_status, occupancy_info, timestamp)
        
        # 7. 결과 저장 (JSON 형식)
        self.save_analysis_result(slot_status, occupancy_info, timestamp)
        
        if success:
            logger.info("분석 및 전송 완료")
        else:
            logger.warning("분석 완료, 백엔드 전송 실패")

def main():
    """메인 함수"""
    analyzer = ParkingOccupancyAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main() 