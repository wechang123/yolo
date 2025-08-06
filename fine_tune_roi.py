#!/usr/bin/env python3
"""
ROI 좌표 미세 조정
이미지를 보고 주차장 흰색 선과 정확히 맞춥니다.
"""

import json
import cv2
import numpy as np

def fine_tune_roi_coordinates():
    """ROI 좌표를 미세 조정"""
    
    # 원본 ROI 로드
    with open("roi_full_rect_coords.json", 'r', encoding='utf-8') as f:
        roi_data = json.load(f)
    
    # 영상 크기
    video_width, video_height = 1920, 1080
    
    # ROI 원본 크기 추정
    image_key = list(roi_data.keys())[0]
    slots = roi_data[image_key]
    
    all_x = []
    all_y = []
    for slot in slots:
        for coord in slot['coords']:
            all_x.append(coord[0])
            all_y.append(coord[1])
    
    original_width = max(all_x)
    original_height = max(all_y)
    
    print(f"원본 크기: {original_width}x{original_height}")
    print(f"영상 크기: {video_width}x{video_height}")
    
    # 이미지 분석 결과를 바탕으로 더 정확한 조정
    # y축을 더 많이 위로 이동하고, x축도 약간 조정
    y_offset = 400  # 400픽셀 위로 이동
    x_scale_factor = 0.95  # x축을 95%로 축소
    
    adjusted_roi_data = {}
    
    for image_key, slots in roi_data.items():
        adjusted_slots = []
        
        for slot in slots:
            adjusted_coords = []
            
            for coord in slot['coords']:
                x, y = coord
                
                # 비율 조정
                x_ratio = x / original_width
                y_ratio = y / original_height
                
                # 새로운 크기에 맞게 조정
                new_x = int(x_ratio * video_width * x_scale_factor)
                new_y = int(y_ratio * video_height) - y_offset
                
                # 좌표가 이미지 범위 내에 있는지 확인
                new_x = max(0, min(new_x, video_width - 1))
                new_y = max(0, min(new_y, video_height - 1))
                
                adjusted_coords.append([new_x, new_y])
            
            adjusted_slots.append({
                'slot_id': slot['slot_id'],
                'coords': adjusted_coords
            })
        
        adjusted_roi_data[image_key] = adjusted_slots
    
    # 저장
    with open("roi_fine_tuned_coords.json", 'w', encoding='utf-8') as f:
        json.dump(adjusted_roi_data, f, ensure_ascii=False, indent=4)
    
    print(f"✅ 미세 조정된 ROI 저장: roi_fine_tuned_coords.json")
    print(f"   - y축 {y_offset}픽셀 위로 이동")
    print(f"   - x축 {x_scale_factor*100}%로 축소")
    
    # 미리보기 생성
    cap = cv2.VideoCapture("IMG_8344.MOV")
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        # 조정된 ROI 시각화
        result_image = frame.copy()
        
        for slot in adjusted_slots:
            coords = slot['coords']
            slot_id = slot['slot_id']
            
            # 다각형 그리기
            pts = np.array(coords, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(result_image, [pts], True, (0, 255, 0), 2)
            
            # 슬롯 ID 표시
            center_x = sum(coord[0] for coord in coords) // len(coords)
            center_y = sum(coord[1] for coord in coords) // len(coords)
            cv2.putText(result_image, slot_id, (center_x-20, center_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        cv2.imwrite("roi_fine_tuned_preview.jpg", result_image)
        print("✅ 미세 조정 미리보기 저장: roi_fine_tuned_preview.jpg")
        
        # 원본과 비교 이미지도 생성
        comparison_image = frame.copy()
        
        # 원본 ROI (빨간색)
        for slot in slots:
            coords = slot['coords']
            pts = np.array(coords, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(comparison_image, [pts], True, (0, 0, 255), 2)
        
        # 조정된 ROI (초록색)
        for slot in adjusted_slots:
            coords = slot['coords']
            pts = np.array(coords, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(comparison_image, [pts], True, (0, 255, 0), 2)
        
        cv2.imwrite("roi_comparison.jpg", comparison_image)
        print("✅ 비교 이미지 저장: roi_comparison.jpg")

def create_interactive_adjustment():
    """대화형 조정 도구"""
    print("\n🔧 대화형 ROI 조정")
    print("=" * 30)
    
    y_offset = int(input("y축 오프셋 (위로 이동할 픽셀 수): "))
    x_scale = float(input("x축 스케일 (0.8-1.2, 기본 1.0): ") or "1.0")
    
    # 원본 ROI 로드
    with open("roi_full_rect_coords.json", 'r', encoding='utf-8') as f:
        roi_data = json.load(f)
    
    # 영상 크기
    video_width, video_height = 1920, 1080
    
    # ROI 원본 크기 추정
    image_key = list(roi_data.keys())[0]
    slots = roi_data[image_key]
    
    all_x = []
    all_y = []
    for slot in slots:
        for coord in slot['coords']:
            all_x.append(coord[0])
            all_y.append(coord[1])
    
    original_width = max(all_x)
    original_height = max(all_y)
    
    adjusted_roi_data = {}
    
    for image_key, slots in roi_data.items():
        adjusted_slots = []
        
        for slot in slots:
            adjusted_coords = []
            
            for coord in slot['coords']:
                x, y = coord
                
                # 비율 조정
                x_ratio = x / original_width
                y_ratio = y / original_height
                
                # 새로운 크기에 맞게 조정
                new_x = int(x_ratio * video_width * x_scale)
                new_y = int(y_ratio * video_height) - y_offset
                
                # 좌표가 이미지 범위 내에 있는지 확인
                new_x = max(0, min(new_x, video_width - 1))
                new_y = max(0, min(new_y, video_height - 1))
                
                adjusted_coords.append([new_x, new_y])
            
            adjusted_slots.append({
                'slot_id': slot['slot_id'],
                'coords': adjusted_coords
            })
        
        adjusted_roi_data[image_key] = adjusted_slots
    
    # 저장
    output_path = f"roi_adjusted_y{y_offset}_x{x_scale}.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(adjusted_roi_data, f, ensure_ascii=False, indent=4)
    
    print(f"✅ 조정된 ROI 저장: {output_path}")
    
    # 미리보기 생성
    cap = cv2.VideoCapture("IMG_8344.MOV")
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        result_image = frame.copy()
        
        for slot in adjusted_slots:
            coords = slot['coords']
            slot_id = slot['slot_id']
            
            pts = np.array(coords, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(result_image, [pts], True, (0, 255, 0), 2)
            
            center_x = sum(coord[0] for coord in coords) // len(coords)
            center_y = sum(coord[1] for coord in coords) // len(coords)
            cv2.putText(result_image, slot_id, (center_x-20, center_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        preview_path = f"roi_preview_y{y_offset}_x{x_scale}.jpg"
        cv2.imwrite(preview_path, result_image)
        print(f"✅ 미리보기 저장: {preview_path}")

if __name__ == "__main__":
    print("🔧 ROI 미세 조정 도구")
    print("=" * 50)
    print("1. 자동 미세 조정")
    print("2. 대화형 조정")
    
    choice = input("선택하세요 (1-2): ")
    
    if choice == "1":
        fine_tune_roi_coordinates()
    elif choice == "2":
        create_interactive_adjustment()
    else:
        print("❌ 잘못된 선택입니다.") 