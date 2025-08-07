#!/usr/bin/env python3
"""
주차장 점유 현황 분석 디버그 버전
IoU 계산 과정을 자세히 보여줌
"""

import cv2
import json
import numpy as np
from datetime import datetime
import logging
from typing import List, Dict, Tuple, Optional
import os
from shapely.geometry import box, Polygon

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_occupancy.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DebugOccupancyAnalyzer:
    def __init__(self, 
                 roi_path: str = "roi_manual_coords.json",
                 image_path: str = "frame_30min.jpg"):
        """
        디버그용 주차장 점유 현황 분석기 초기화
        """
        self.roi_path = roi_path
        self.image_path = image_path
        
        # 초기화
        self.roi_data = self.load_roi_data()
        
        logger.info(f"디버그 분석기 초기화 완료")
        
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
    
    def load_yolo_detections(self) -> List[Dict]:
        """YOLO 인식 결과 로드"""
        # 최신 인식 결과 파일 찾기
        txt_file = f"runs/detect/occupancy_analysis3/labels/frame_30min.txt"
        
        if not os.path.exists(txt_file):
            logger.error(f"인식 결과 파일이 없습니다: {txt_file}")
            return []
        
        detections = []
        with open(txt_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
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
                        'line_num': line_num,
                        'class_id': class_id,
                        'x_center': x_center,
                        'y_center': y_center,
                        'width': width,
                        'height': height,
                        'confidence': confidence
                    })
        
        logger.info(f"YOLO 인식 결과 로드 완료: {len(detections)}개 객체")
        return detections
    
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
                'line_num': det['line_num'],
                'class_id': det['class_id'],
                'confidence': det['confidence'],
                'bbox': [x1, y1, x2, y2],
                'center': [x_center_px, y_center_px],
                'bbox_area': w_px * h_px
            })
        
        return normalized_detections
    
    def calculate_iou(self, bbox: List[float], roi_coords: List[List[int]]) -> float:
        """IoU 계산 함수"""
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
    
    def debug_parking_slots(self, detections: List[Dict]):
        """주차 슬롯별 점유 현황 디버그 분석"""
        # 이미지 로드하여 크기 확인
        image = cv2.imread(self.image_path)
        if image is None:
            logger.error(f"이미지를 로드할 수 없습니다: {self.image_path}")
            return
        
        height, width = image.shape[:2]
        logger.info(f"이미지 크기: {width}x{height}")
        
        normalized_detections = self.normalize_coordinates(detections, (height, width))
        
        # ROI 데이터에서 frame_30min.jpg의 슬롯 정보 사용
        image_key = "frame_30min.jpg"
        slots = self.roi_data.get(image_key, [])
        
        logger.info(f"=== 디버그 분석 시작 ===")
        logger.info(f"총 감지된 차량: {len(normalized_detections)}대")
        logger.info(f"총 주차 슬롯: {len(slots)}개")
        
        # 각 차량의 위치와 크기 정보 출력
        logger.info(f"\n=== 감지된 차량 정보 ===")
        for i, det in enumerate(normalized_detections, 1):
            logger.info(f"차량 {i} (라인 {det['line_num']}): "
                       f"중심점({det['center'][0]}, {det['center'][1]}), "
                       f"바운딩박스({det['bbox'][0]},{det['bbox'][1]},{det['bbox'][2]},{det['bbox'][3]}), "
                       f"면적={det['bbox_area']}")
        
        # 각 슬롯별 IoU 계산 결과
        logger.info(f"\n=== 슬롯별 IoU 분석 ===")
        
        occupied_slots = []
        free_slots = []
        
        for slot in slots:
            slot_id = slot['slot_id']
            coords = slot['coords']
            
            # ROI 면적 계산
            roi_poly = Polygon(coords)
            roi_area = roi_poly.area
            
            # 각 차량과의 IoU 계산
            max_iou = 0.0
            best_vehicle = None
            
            for det in normalized_detections:
                iou = self.calculate_iou(det['bbox'], coords)
                if iou > max_iou:
                    max_iou = iou
                    best_vehicle = det
            
            # 점유 판단
            occupied = max_iou >= 0.17
            
            slot_info = {
                'slot_id': slot_id,
                'occupied': occupied,
                'max_iou': max_iou,
                'roi_area': roi_area,
                'best_vehicle': best_vehicle
            }
            
            if occupied:
                occupied_slots.append(slot_info)
            else:
                free_slots.append(slot_info)
            
            logger.info(f"{slot_id}: IoU={max_iou:.3f}, "
                       f"ROI면적={roi_area:.0f}, "
                       f"점유={'O' if occupied else 'X'}")
            
            if best_vehicle:
                logger.info(f"  -> 최고 IoU 차량: 라인 {best_vehicle['line_num']}, "
                           f"중심점({best_vehicle['center'][0]}, {best_vehicle['center'][1]})")
        
        # 요약 정보
        logger.info(f"\n=== 분석 요약 ===")
        logger.info(f"감지된 차량: {len(normalized_detections)}대")
        logger.info(f"점유 슬롯: {len(occupied_slots)}개")
        logger.info(f"빈 슬롯: {len(free_slots)}개")
        logger.info(f"점유율: {len(occupied_slots)}/{len(slots)} ({len(occupied_slots)/len(slots)*100:.1f}%)")
        
        # 점유되지 않은 차량들
        occupied_vehicles = set()
        for slot in occupied_slots:
            if slot['best_vehicle']:
                occupied_vehicles.add(slot['best_vehicle']['line_num'])
        
        unoccupied_vehicles = [det for det in normalized_detections if det['line_num'] not in occupied_vehicles]
        
        logger.info(f"\n=== 점유되지 않은 차량들 ===")
        logger.info(f"점유되지 않은 차량: {len(unoccupied_vehicles)}대")
        for det in unoccupied_vehicles:
            logger.info(f"라인 {det['line_num']}: 중심점({det['center'][0]}, {det['center'][1]}), "
                       f"바운딩박스({det['bbox'][0]},{det['bbox'][1]},{det['bbox'][2]},{det['bbox'][3]})")
        
        return {
            'total_vehicles': len(normalized_detections),
            'occupied_slots': len(occupied_slots),
            'free_slots': len(free_slots),
            'total_slots': len(slots),
            'unoccupied_vehicles': len(unoccupied_vehicles),
            'occupied_slots_detail': occupied_slots,
            'free_slots_detail': free_slots
        }
    
    def run_debug_analysis(self):
        """디버그 분석 실행"""
        logger.info("디버그 분석 시작")
        
        # 1. YOLO 인식 결과 로드
        detections = self.load_yolo_detections()
        if not detections:
            logger.error("YOLO 인식 결과 로드 실패")
            return
        
        # 2. 디버그 분석 실행
        result = self.debug_parking_slots(detections)
        
        logger.info("디버그 분석 완료")
        return result

def main():
    """메인 함수"""
    analyzer = DebugOccupancyAnalyzer()
    analyzer.run_debug_analysis()

if __name__ == "__main__":
    main()
