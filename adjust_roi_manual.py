#!/usr/bin/env python3
"""
수동 ROI 좌표 조정
더 큰 오프셋으로 ROI를 위로 이동시킵니다.
"""

import json
import cv2
import numpy as np

def adjust_roi_with_offset():
    """큰 오프셋으로 ROI 조정"""
    
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
    
    # 큰 오프셋 적용 (300픽셀 위로)
    y_offset = 300
    
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
                new_x = int(x_ratio * video_width)
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
    with open("roi_adjusted_coords.json", 'w', encoding='utf-8') as f:
        json.dump(adjusted_roi_data, f, ensure_ascii=False, indent=4)
    
    print(f"✅ {y_offset}픽셀 위로 이동된 ROI 저장 완료")
    
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
        
        cv2.imwrite("roi_preview_300px_up.jpg", result_image)
        print("✅ 미리보기 저장: roi_preview_300px_up.jpg")

if __name__ == "__main__":
    adjust_roi_with_offset() 