#!/usr/bin/env python3
"""
ROI 좌표 조정 스크립트
영상 이미지 크기에 맞게 ROI 좌표를 조정합니다.
"""

import json
import cv2
import numpy as np
from typing import Dict, List

def load_roi_data(roi_path: str) -> Dict:
    """ROI 데이터 로드"""
    with open(roi_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_roi_data(roi_data: Dict, output_path: str):
    """ROI 데이터 저장"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(roi_data, f, ensure_ascii=False, indent=4)

def adjust_coordinates(coords: List[List[int]], 
                      original_size: tuple, 
                      target_size: tuple,
                      y_offset: int = 0) -> List[List[int]]:
    """
    좌표를 새로운 이미지 크기에 맞게 조정
    
    Args:
        coords: 원본 좌표 리스트 [[x1, y1], [x2, y2], ...]
        original_size: 원본 이미지 크기 (width, height)
        target_size: 대상 이미지 크기 (width, height)
        y_offset: y축 오프셋 (위로 이동할 픽셀 수)
    """
    adjusted_coords = []
    
    for coord in coords:
        x, y = coord
        
        # 비율 조정
        x_ratio = x / original_size[0]
        y_ratio = y / original_size[1]
        
        # 새로운 크기에 맞게 조정
        new_x = int(x_ratio * target_size[0])
        new_y = int(y_ratio * target_size[1]) - y_offset
        
        # 좌표가 이미지 범위 내에 있는지 확인
        new_x = max(0, min(new_x, target_size[0] - 1))
        new_y = max(0, min(new_y, target_size[1] - 1))
        
        adjusted_coords.append([new_x, new_y])
    
    return adjusted_coords

def visualize_roi_on_frame(frame: np.ndarray, roi_data: Dict, image_key: str = "test.png"):
    """프레임에 ROI를 시각화"""
    result_image = frame.copy()
    
    if image_key in roi_data:
        slots = roi_data[image_key]
        
        for i, slot in enumerate(slots):
            coords = slot['coords']
            slot_id = slot['slot_id']
            
            # 다각형 그리기
            pts = np.array(coords, np.int32)
            pts = pts.reshape((-1, 1, 2))
            
            # 색상 (슬롯별로 다른 색상)
            color = (0, 255, 0)  # 녹색
            
            cv2.polylines(result_image, [pts], True, color, 2)
            
            # 슬롯 ID 표시
            center_x = sum(coord[0] for coord in coords) // len(coords)
            center_y = sum(coord[1] for coord in coords) // len(coords)
            
            cv2.putText(result_image, slot_id, (center_x-20, center_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    return result_image

def main():
    """메인 함수"""
    print("🔧 ROI 좌표 조정 도구")
    print("=" * 50)
    
    # 파일 경로
    roi_path = "roi_full_rect_coords.json"
    video_path = "IMG_8344.MOV"
    
    # ROI 데이터 로드
    print("📁 ROI 데이터 로드 중...")
    roi_data = load_roi_data(roi_path)
    
    # 영상 정보 가져오기
    print("🎬 영상 정보 확인 중...")
    cap = cv2.VideoCapture(video_path)
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    
    print(f"영상 크기: {video_width}x{video_height}")
    
    # 원본 이미지 크기 추정 (ROI 좌표 기반)
    image_key = list(roi_data.keys())[0]
    slots = roi_data[image_key]
    
    # ROI 좌표에서 최대/최소 값 찾기
    all_x = []
    all_y = []
    for slot in slots:
        for coord in slot['coords']:
            all_x.append(coord[0])
            all_y.append(coord[1])
    
    original_width = max(all_x)
    original_height = max(all_y)
    
    print(f"ROI 원본 크기 추정: {original_width}x{original_height}")
    
    # 조정 옵션
    print("\n🔧 조정 옵션:")
    print("1. 자동 조정 (비율 기반)")
    print("2. 수동 조정 (y축 오프셋)")
    print("3. 미리보기")
    
    choice = input("선택하세요 (1-3): ")
    
    if choice == "1":
        # 자동 조정
        print("\n🔄 자동 조정 중...")
        adjusted_roi_data = {}
        
        for image_key, slots in roi_data.items():
            adjusted_slots = []
            
            for slot in slots:
                adjusted_coords = adjust_coordinates(
                    slot['coords'], 
                    (original_width, original_height), 
                    (video_width, video_height)
                )
                
                adjusted_slots.append({
                    'slot_id': slot['slot_id'],
                    'coords': adjusted_coords
                })
            
            adjusted_roi_data[image_key] = adjusted_slots
        
        # 저장
        output_path = "roi_adjusted_coords.json"
        save_roi_data(adjusted_roi_data, output_path)
        print(f"✅ 조정된 ROI 저장: {output_path}")
        
    elif choice == "2":
        # 수동 조정
        y_offset = int(input("y축 오프셋 (위로 이동할 픽셀 수): "))
        
        print(f"\n🔄 y축 {y_offset}픽셀 위로 이동 중...")
        adjusted_roi_data = {}
        
        for image_key, slots in roi_data.items():
            adjusted_slots = []
            
            for slot in slots:
                adjusted_coords = adjust_coordinates(
                    slot['coords'], 
                    (original_width, original_height), 
                    (video_width, video_height),
                    y_offset
                )
                
                adjusted_slots.append({
                    'slot_id': slot['slot_id'],
                    'coords': adjusted_coords
                })
            
            adjusted_roi_data[image_key] = adjusted_slots
        
        # 저장
        output_path = "roi_adjusted_coords.json"
        save_roi_data(adjusted_roi_data, output_path)
        print(f"✅ 조정된 ROI 저장: {output_path}")
        
    elif choice == "3":
        # 미리보기
        print("\n👀 미리보기 생성 중...")
        
        # 첫 번째 프레임 추출
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            # ROI 시각화
            result_image = visualize_roi_on_frame(frame, roi_data)
            
            # 저장
            cv2.imwrite("roi_preview.jpg", result_image)
            print("✅ 미리보기 저장: roi_preview.jpg")
            
            # 조정된 버전도 생성
            y_offset = 100  # 예시로 100픽셀 위로 이동
            adjusted_roi_data = {}
            
            for image_key, slots in roi_data.items():
                adjusted_slots = []
                
                for slot in slots:
                    adjusted_coords = adjust_coordinates(
                        slot['coords'], 
                        (original_width, original_height), 
                        (video_width, video_height),
                        y_offset
                    )
                    
                    adjusted_slots.append({
                        'slot_id': slot['slot_id'],
                        'coords': adjusted_coords
                    })
                
                adjusted_roi_data[image_key] = adjusted_slots
            
            # 조정된 ROI 시각화
            adjusted_result = visualize_roi_on_frame(frame, adjusted_roi_data)
            cv2.imwrite("roi_preview_adjusted.jpg", adjusted_result)
            print("✅ 조정된 미리보기 저장: roi_preview_adjusted.jpg")
            
            # 조정된 ROI 저장
            save_roi_data(adjusted_roi_data, "roi_adjusted_coords.json")
            print("✅ 조정된 ROI 저장: roi_adjusted_coords.json")
    
    else:
        print("❌ 잘못된 선택입니다.")
        return
    
    print("\n🎯 다음 단계:")
    print("1. 조정된 ROI 파일을 확인하세요: roi_adjusted_coords.json")
    print("2. 미리보기 이미지를 확인하세요: roi_preview*.jpg")
    print("3. parking_analysis_system.py에서 roi_path를 'roi_adjusted_coords.json'으로 변경하세요")

if __name__ == "__main__":
    main() 