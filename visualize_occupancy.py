#!/usr/bin/env python3
"""
주차장 점유 현황 시각화 및 IoU 조정 도구
비어있으면 초록, 차있으면 빨강으로 시각화
"""

import cv2
import json
import numpy as np
from datetime import datetime
import logging
from typing import List, Dict, Tuple, Optional
import os
import argparse
from shapely.geometry import box, Polygon

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('visualize_occupancy.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OccupancyVisualizer:
    def __init__(self, 
                 roi_path: str = "roi_manual_coords.json",
                 image_path: str = "frame_30min.jpg",
                 iou_threshold: float = 0.17):
        """
        주차장 점유 현황 시각화기 초기화
        """
        self.roi_path = roi_path
        self.image_path = image_path
        self.iou_threshold = iou_threshold
        
        # 초기화
        self.roi_data = self.load_roi_data()
        self.image = cv2.imread(self.image_path)
        
        if self.image is None:
            raise ValueError(f"이미지를 로드할 수 없습니다: {self.image_path}")
        
        self.height, self.width = self.image.shape[:2]
        logger.info(f"이미지 크기: {self.width}x{self.height}")
        logger.info(f"IoU 임계값: {self.iou_threshold}")
        
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
    
    def normalize_coordinates(self, detections: List[Dict]) -> List[Dict]:
        """좌표를 픽셀 단위로 변환"""
        normalized_detections = []
        
        for det in detections:
            # YOLO 좌표를 픽셀 좌표로 변환
            x_center_px = int(det['x_center'] * self.width)
            y_center_px = int(det['y_center'] * self.height)
            w_px = int(det['width'] * self.width)
            h_px = int(det['height'] * self.height)
            
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
    
    def analyze_occupancy(self, detections: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """주차 슬롯별 점유 현황 분석"""
        normalized_detections = self.normalize_coordinates(detections)
        
        # ROI 데이터에서 frame_30min.jpg의 슬롯 정보 사용
        image_key = "frame_30min.jpg"
        slots = self.roi_data.get(image_key, [])
        
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
            occupied = max_iou >= self.iou_threshold
            
            slot_info = {
                'slot_id': slot_id,
                'occupied': occupied,
                'max_iou': max_iou,
                'roi_area': roi_area,
                'best_vehicle': best_vehicle,
                'coords': coords
            }
            
            if occupied:
                occupied_slots.append(slot_info)
            else:
                free_slots.append(slot_info)
        
        return occupied_slots, free_slots
    
    def visualize_occupancy(self, occupied_slots: List[Dict], free_slots: List[Dict], 
                          show_vehicles: bool = True, output_path: str = None):
        """주차장 점유 현황 시각화"""
        # 이미지 복사
        vis_image = self.image.copy()
        
        # 색상 정의
        GREEN = (0, 255, 0)    # 비어있음 (초록)
        RED = (0, 0, 255)      # 점유됨 (빨강)
        YELLOW = (0, 255, 255) # 텍스트
        
        # 점유된 슬롯 그리기 (빨강)
        for slot in occupied_slots:
            coords = slot['coords']
            pts = np.array(coords, np.int32)
            pts = pts.reshape((-1, 1, 2))
            
            # 다각형 그리기
            cv2.polylines(vis_image, [pts], True, RED, 2)
            
            # 텍스트 추가
            text = f"{slot['slot_id']} (IoU:{slot['max_iou']:.2f})"
            cv2.putText(vis_image, text, (coords[0][0], coords[0][1] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, RED, 1)
        
        # 비어있는 슬롯 그리기 (초록)
        for slot in free_slots:
            coords = slot['coords']
            pts = np.array(coords, np.int32)
            pts = pts.reshape((-1, 1, 2))
            
            # 다각형 그리기
            cv2.polylines(vis_image, [pts], True, GREEN, 2)
            
            # 텍스트 추가
            text = f"{slot['slot_id']} (IoU:{slot['max_iou']:.2f})"
            cv2.putText(vis_image, text, (coords[0][0], coords[0][1] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, GREEN, 1)
        
        # 통계 정보 추가
        total_slots = len(occupied_slots) + len(free_slots)
        occupancy_rate = len(occupied_slots) / total_slots * 100 if total_slots > 0 else 0
        
        stats_text = f"Occupancy: {len(occupied_slots)}/{total_slots} ({occupancy_rate:.1f}%) | IoU Threshold: {self.iou_threshold}"
        cv2.putText(vis_image, stats_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, YELLOW, 2)
        
        # 범례 추가
        legend_y = 60
        cv2.putText(vis_image, "Green: Empty", (10, legend_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, GREEN, 2)
        cv2.putText(vis_image, "Red: Occupied", (10, legend_y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, RED, 2)
        
        # 결과 출력
        if output_path:
            cv2.imwrite(output_path, vis_image)
            logger.info(f"시각화 결과 저장: {output_path}")
        
        return vis_image
    
    def find_optimal_iou(self, detections: List[Dict], target_occupancy: float = None):
        """최적의 IoU 임계값 찾기"""
        logger.info("최적 IoU 임계값 찾기 시작...")
        
        iou_values = np.arange(0.01, 0.51, 0.01)  # 0.01부터 0.5까지 0.01씩
        results = []
        
        for iou_threshold in iou_values:
            self.iou_threshold = iou_threshold
            occupied_slots, free_slots = self.analyze_occupancy(detections)
            
            total_slots = len(occupied_slots) + len(free_slots)
            occupancy_rate = len(occupied_slots) / total_slots * 100 if total_slots > 0 else 0
            
            results.append({
                'iou_threshold': iou_threshold,
                'occupied_slots': len(occupied_slots),
                'total_slots': total_slots,
                'occupancy_rate': occupancy_rate
            })
            
            logger.info(f"IoU {iou_threshold:.2f}: {len(occupied_slots)}/{total_slots} ({occupancy_rate:.1f}%)")
        
        # 결과 출력
        logger.info("\n=== IoU 임계값별 결과 ===")
        for result in results:
            logger.info(f"IoU {result['iou_threshold']:.2f}: "
                       f"{result['occupied_slots']}/{result['total_slots']} "
                       f"({result['occupancy_rate']:.1f}%)")
        
        return results
    
    def run_visualization(self, show_vehicles: bool = True, output_path: str = None):
        """시각화 실행"""
        logger.info("주차장 점유 현황 시각화 시작")
        
        # 1. YOLO 인식 결과 로드
        detections = self.load_yolo_detections()
        if not detections:
            logger.error("YOLO 인식 결과 로드 실패")
            return
        
        # 2. 점유 현황 분석
        occupied_slots, free_slots = self.analyze_occupancy(detections)
        
        # 3. 결과 출력
        total_slots = len(occupied_slots) + len(free_slots)
        occupancy_rate = len(occupied_slots) / total_slots * 100 if total_slots > 0 else 0
        
        logger.info(f"=== 분석 결과 ===")
        logger.info(f"감지된 차량: {len(detections)}대")
        logger.info(f"점유 슬롯: {len(occupied_slots)}개")
        logger.info(f"빈 슬롯: {len(free_slots)}개")
        logger.info(f"점유율: {len(occupied_slots)}/{total_slots} ({occupancy_rate:.1f}%)")
        logger.info(f"IoU 임계값: {self.iou_threshold}")
        
        # 4. 시각화
        vis_image = self.visualize_occupancy(occupied_slots, free_slots, show_vehicles, output_path)
        
        return vis_image, occupied_slots, free_slots

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='주차장 점유 현황 시각화 및 IoU 조정')
    parser.add_argument('--iou', type=float, default=0.1, help='IoU 임계값 (기본값: 0.1)')
    parser.add_argument('--no-vehicles', action='store_true', help='차량 바운딩 박스 숨기기')
    parser.add_argument('--output', type=str, help='출력 이미지 경로')
    parser.add_argument('--find-optimal', action='store_true', help='최적 IoU 임계값 찾기')
    parser.add_argument('--target-occupancy', type=float, help='목표 점유율 (%)')
    
    args = parser.parse_args()
    
    try:
        # 시각화기 초기화
        visualizer = OccupancyVisualizer(iou_threshold=args.iou)
        
        if args.find_optimal:
            # 최적 IoU 임계값 찾기
            detections = visualizer.load_yolo_detections()
            if detections:
                results = visualizer.find_optimal_iou(detections, args.target_occupancy)
        else:
            # 시각화 실행
            output_path = args.output or f"occupancy_visualization_iou{args.iou:.2f}.jpg"
            vis_image, occupied_slots, free_slots = visualizer.run_visualization(
                show_vehicles=not args.no_vehicles, 
                output_path=output_path
            )
            
            logger.info(f"시각화 완료: {output_path}")
            
    except Exception as e:
        logger.error(f"오류 발생: {e}")

if __name__ == "__main__":
    main()
