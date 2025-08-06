#!/usr/bin/env python3
"""
주차장 영상 분석 및 백엔드 전송 시스템
1시간 영상에서 3분마다 프레임 추출 → YOLO 차량 인식 → ROI 비교 → 백엔드 전송
"""

import cv2
import json
import time
import requests
import numpy as np
from datetime import datetime, timedelta
import torch
from models.experimental import attempt_load
from utils.general import non_max_suppression, scale_boxes
# from utils.plots import plot_one_box  # 사용하지 않으므로 주석 처리
import threading
import logging
from typing import List, Dict, Tuple, Optional

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('parking_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ParkingAnalysisSystem:
    def __init__(self, 
                 video_path: str = "IMG_8344.MOV",
                 roi_path: str = "roi_full_rect_coords.json",
                 model_path: str = "best_macos.pt",
                 backend_url: str = "http://localhost:8080",
                 interval_minutes: int = 3):
        """
        주차장 분석 시스템 초기화
        
        Args:
            video_path: 분석할 영상 파일 경로
            roi_path: ROI 좌표 JSON 파일 경로
            model_path: YOLO 모델 파일 경로
            backend_url: 백엔드 서버 URL
            interval_minutes: 프레임 추출 간격 (분)
        """
        self.video_path = video_path
        self.roi_path = roi_path
        self.model_path = model_path
        self.backend_url = backend_url
        self.interval_minutes = interval_minutes
        self.interval_seconds = interval_minutes * 60
        
        # 초기화
        self.roi_data = self.load_roi_data()
        self.model = self.load_yolo_model()
        self.video_info = self.get_video_info()
        
        logger.info(f"시스템 초기화 완료 - 영상 길이: {self.video_info['duration_minutes']:.1f}분")
        
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
            device = 'mps' if torch.backends.mps.is_available() else 'cpu'
            model = attempt_load(self.model_path, device=device)
            model.eval()
            logger.info(f"YOLO 모델 로드 완료 - 장치: {device}")
            return model
        except Exception as e:
            logger.error(f"YOLO 모델 로드 실패: {e}")
            return None
    
    def get_video_info(self) -> Dict:
        """영상 정보 가져오기"""
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise ValueError(f"영상을 열 수 없습니다: {self.video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_seconds = total_frames / fps
        duration_minutes = duration_seconds / 60
        
        cap.release()
        
        return {
            'fps': fps,
            'total_frames': total_frames,
            'duration_seconds': duration_seconds,
            'duration_minutes': duration_minutes
        }
    
    def extract_frame_at_time(self, target_seconds: float) -> Optional[np.ndarray]:
        """지정된 시간에 해당하는 프레임 추출"""
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            logger.error("영상을 열 수 없습니다")
            return None
        
        # 목표 시간에 해당하는 프레임 번호 계산
        target_frame = int(target_seconds * self.video_info['fps'])
        
        # 해당 프레임으로 이동
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            logger.info(f"프레임 추출 완료 - 시간: {target_seconds:.1f}초")
            return frame
        else:
            logger.error(f"프레임 추출 실패 - 시간: {target_seconds:.1f}초")
            return None
    
    def detect_vehicles(self, frame: np.ndarray) -> List[Dict]:
        """YOLO를 사용하여 차량 탐지 (YOLO 기본 구현과 동일)"""
        if self.model is None:
            logger.error("YOLO 모델이 로드되지 않았습니다")
            return []
        
        try:
            # 이미지 전처리 (YOLO 기본 구현과 동일)
            img = cv2.resize(frame, (640, 640))
            img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
            img = np.ascontiguousarray(img)
            img = torch.from_numpy(img).float()
            img /= 255.0  # 0 - 255 to 0.0 - 1.0
            if len(img.shape) == 3:
                img = img[None]  # expand for batch dim
            
            # 모델과 같은 장치로 이동
            device = next(self.model.parameters()).device
            img = img.to(device)
            
            # 추론 (YOLO 기본 구현과 동일)
            with torch.no_grad():
                pred = self.model(img, augment=False, visualize=False)
                pred = non_max_suppression(pred, conf_thres=0.3, iou_thres=0.5, max_det=1000)
            
            detections = []
            # YOLO 기본 구현과 동일하게 pred 전체를 처리
            for i, det in enumerate(pred):
                if det is not None:
                    # 원본 이미지 크기로 좌표 변환 (YOLO 기본 구현과 동일)
                    det[:, :4] = scale_boxes(img.shape[2:], det[:, :4], frame.shape).round()
                    
                    for *xyxy, conf, cls in det:
                        x1, y1, x2, y2 = map(int, xyxy)
                        detections.append({
                            'bbox': [x1, y1, x2, y2],
                            'confidence': float(conf),
                            'class': int(cls)
                        })
            
            logger.info(f"차량 탐지 완료 - {len(detections)}대 탐지")
            return detections
            
        except Exception as e:
            logger.error(f"차량 탐지 실패: {e}")
            return []
    
    def check_parking_slots(self, frame: np.ndarray, detections: List[Dict]) -> List[Dict]:
        """ROI와 차량 탐지 결과를 비교하여 주차 슬롯 상태 확인"""
        slot_status = []
        
        # ROI 데이터에서 슬롯 정보 가져오기 (첫 번째 이미지 사용)
        image_key = list(self.roi_data.keys())[0]  # "test.png"
        slots = self.roi_data[image_key]
        
        for slot in slots:
            slot_id = slot['slot_id']
            roi_coords = slot['coords']
            
            # ROI 영역 내 차량 개수 확인
            vehicles_in_slot = 0
            
            for detection in detections:
                bbox = detection['bbox']
                vehicle_center = [(bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2]
                
                # 차량 중심점이 ROI 내부에 있는지 확인
                if self.point_in_polygon(vehicle_center, roi_coords):
                    vehicles_in_slot += 1
            
            # 주차 슬롯 상태 결정 (차량이 있으면 occupied, 없으면 available)
            is_available = vehicles_in_slot == 0
            
            slot_status.append({
                'slot_id': slot_id,
                'is_available': is_available,
                'vehicle_count': vehicles_in_slot,
                'roi_coords': roi_coords
            })
        
        logger.info(f"주차 슬롯 상태 분석 완료 - {len(slot_status)}개 슬롯")
        return slot_status
    
    def point_in_polygon(self, point: List[int], polygon: List[List[int]]) -> bool:
        """점이 다각형 내부에 있는지 확인 (Ray casting algorithm)"""
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def send_to_backend(self, slot_status: List[Dict], timestamp: datetime) -> bool:
        """백엔드 서버로 주차 슬롯 상태 전송"""
        try:
            # API 요청 데이터 준비
            parking_lot_id = 1  # 기본 주차장 ID
            
            for slot in slot_status:
                slot_number = int(slot['slot_id'].split('_')[1])  # "slot_2" -> 2
                
                request_data = {
                    'parkingLotId': parking_lot_id,
                    'slotNumber': slot_number,
                    'isAvailable': slot['is_available']
                }
                
                # PUT 요청으로 주차 슬롯 상태 업데이트
                response = requests.put(
                    f"{self.backend_url}/parking-slots",
                    json=request_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                if response.status_code == 200:
                    logger.info(f"슬롯 {slot_number} 상태 전송 성공: {'사용가능' if slot['is_available'] else '사용중'}")
                else:
                    logger.error(f"슬롯 {slot_number} 상태 전송 실패: {response.status_code}")
            
            return True
            
        except Exception as e:
            logger.error(f"백엔드 전송 실패: {e}")
            return False
    
    def save_analysis_result(self, slot_status: List[Dict], timestamp: datetime, frame: np.ndarray):
        """분석 결과를 로컬에 저장"""
        try:
            # 결과 이미지 생성 (ROI와 탐지 결과 시각화)
            result_image = frame.copy()
            
            # ROI 영역 그리기
            for slot in slot_status:
                roi_coords = slot['roi_coords']
                color = (0, 255, 0) if slot['is_available'] else (0, 0, 255)  # 녹색: 사용가능, 빨간색: 사용중
                
                # 다각형 그리기
                pts = np.array(roi_coords, np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(result_image, [pts], True, color, 2)
                
                # 슬롯 ID 표시
                center_x = sum(coord[0] for coord in roi_coords) // len(roi_coords)
                center_y = sum(coord[1] for coord in roi_coords) // len(roi_coords)
                cv2.putText(result_image, slot['slot_id'], (center_x-20, center_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            # 결과 저장
            timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
            cv2.imwrite(f"analysis_results/frame_{timestamp_str}.jpg", result_image)
            
            # JSON 결과 저장
            result_data = {
                'timestamp': timestamp.isoformat(),
                'slot_status': slot_status
            }
            
            with open(f"analysis_results/result_{timestamp_str}.json", 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"분석 결과 저장 완료: {timestamp_str}")
            
        except Exception as e:
            logger.error(f"결과 저장 실패: {e}")
    
    def run_analysis(self):
        """전체 분석 프로세스 실행"""
        logger.info("주차장 영상 분석 시작")
        
        # 결과 저장 디렉토리 생성
        import os
        os.makedirs("analysis_results", exist_ok=True)
        
        # 영상 시작부터 끝까지 3분 간격으로 분석
        current_time = 0.0
        analysis_count = 0
        
        while current_time <= self.video_info['duration_seconds']:
            logger.info(f"분석 진행률: {current_time/self.video_info['duration_seconds']*100:.1f}%")
            
            # 현재 시간에 해당하는 프레임 추출
            frame = self.extract_frame_at_time(current_time)
            if frame is None:
                current_time += self.interval_seconds
                continue
            
            # 차량 탐지
            detections = self.detect_vehicles(frame)
            
            # 주차 슬롯 상태 확인
            slot_status = self.check_parking_slots(frame, detections)
            
            # 현재 시간 계산
            timestamp = datetime.now()
            
            # 백엔드로 전송
            success = self.send_to_backend(slot_status, timestamp)
            
            # 결과 저장
            self.save_analysis_result(slot_status, timestamp, frame)
            
            analysis_count += 1
            logger.info(f"분석 완료 #{analysis_count} - 시간: {current_time/60:.1f}분, 슬롯 상태: {sum(1 for s in slot_status if s['is_available'])}/{len(slot_status)} 사용가능")
            
            # 다음 분석 시간으로 이동
            current_time += self.interval_seconds
        
        logger.info(f"전체 분석 완료 - 총 {analysis_count}회 분석 수행")

def main():
    """메인 실행 함수"""
    try:
        # 시스템 초기화
        system = ParkingAnalysisSystem(
            video_path="IMG_8344.MOV",
                             roi_path="roi_precise_offset_150.json", 
            model_path="best_macos.pt",
            backend_url="http://localhost:8080",  # 백엔드 서버 URL
            interval_minutes=3
        )
        
        # 분석 실행
        system.run_analysis()
        
    except Exception as e:
        logger.error(f"시스템 실행 실패: {e}")
        raise

if __name__ == "__main__":
    main() 