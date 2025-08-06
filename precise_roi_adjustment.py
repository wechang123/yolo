#!/usr/bin/env python3
"""
정확한 ROI 좌표 변환
원본: 2556×1179 픽셀
영상: 1920×1080 픽셀
"""

import json
import cv2
import numpy as np

def precise_roi_conversion():
    """정확한 크기 정보로 ROI 좌표 변환"""
    
    # 원본 ROI 로드
    with open("roi_full_rect_coords.json", 'r', encoding='utf-8') as f:
        roi_data = json.load(f)
    
    # 정확한 크기 정보
    original_width, original_height = 2556, 1179
    video_width, video_height = 1920, 1080
    
    print(f"원본 이미지 크기: {original_width}×{original_height}")
    print(f"영상 크기: {video_width}×{video_height}")
    
    # 비율 계산
    width_ratio = video_width / original_width
    height_ratio = video_height / original_height
    
    print(f"너비 비율: {width_ratio:.3f}")
    print(f"높이 비율: {height_ratio:.3f}")
    
    adjusted_roi_data = {}
    
    for image_key, slots in roi_data.items():
        adjusted_slots = []
        
        for slot in slots:
            adjusted_coords = []
            
            for coord in slot['coords']:
                x, y = coord
                
                # 정확한 비율로 변환
                new_x = int(x * width_ratio)
                new_y = int(y * height_ratio)
                
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
    with open("roi_precise_coords.json", 'w', encoding='utf-8') as f:
        json.dump(adjusted_roi_data, f, ensure_ascii=False, indent=4)
    
    print(f"✅ 정확한 변환된 ROI 저장: roi_precise_coords.json")
    
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
        
        cv2.imwrite("roi_precise_preview.jpg", result_image)
        print("✅ 정확한 변환 미리보기 저장: roi_precise_preview.jpg")
        
        # 좌표 범위 확인
        all_y = []
        for slot in adjusted_slots:
            for coord in slot['coords']:
                all_y.append(coord[1])
        
        print(f"📊 변환된 y좌표 범위: {min(all_y)} ~ {max(all_y)}")
        print(f"📍 영상 기준 위치: {min(all_y)/video_height*100:.1f}% ~ {max(all_y)/video_height*100:.1f}%")

def test_with_offset():
    """오프셋을 적용한 테스트"""
    print("\n🔧 오프셋 테스트")
    print("=" * 30)
    
    # 정확한 변환 후 오프셋 적용
    with open("roi_precise_coords.json", 'r', encoding='utf-8') as f:
        precise_data = json.load(f)
    
    # 오프셋 값들 테스트
    offsets = [0, 50, 100, 150, 200]
    
    for offset in offsets:
        adjusted_data = {}
        
        for image_key, slots in precise_data.items():
            adjusted_slots = []
            
            for slot in slots:
                adjusted_coords = []
                
                for coord in slot['coords']:
                    x, y = coord
                    new_y = y - offset
                    
                    # 좌표가 이미지 범위 내에 있는지 확인
                    new_y = max(0, min(new_y, 1080 - 1))
                    
                    adjusted_coords.append([x, new_y])
                
                adjusted_slots.append({
                    'slot_id': slot['slot_id'],
                    'coords': adjusted_coords
                })
            
            adjusted_data[image_key] = adjusted_slots
        
        # 저장
        output_path = f"roi_precise_offset_{offset}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(adjusted_data, f, ensure_ascii=False, indent=4)
        
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
            
            preview_path = f"roi_precise_offset_{offset}_preview.jpg"
            cv2.imwrite(preview_path, result_image)
            
            # y좌표 범위 확인
            all_y = []
            for slot in adjusted_slots:
                for coord in slot['coords']:
                    all_y.append(coord[1])
            
            print(f"오프셋 {offset}px: y좌표 {min(all_y)}~{max(all_y)} ({min(all_y)/1080*100:.1f}%~{max(all_y)/1080*100:.1f}%)")

if __name__ == "__main__":
    print("🎯 정확한 ROI 좌표 변환")
    print("=" * 50)
    
    # 1. 정확한 변환
    precise_roi_conversion()
    
    # 2. 오프셋 테스트
    test_with_offset()
    
    print("\n✅ 모든 변환 완료!")
    print("📁 생성된 파일들:")
    print("  - roi_precise_coords.json (정확한 변환)")
    print("  - roi_precise_offset_*.json (오프셋 적용)")
    print("  - roi_precise_*_preview.jpg (미리보기)")
    print("\n🎯 다음 단계:")
    print("1. 미리보기 이미지들을 확인하여 가장 적합한 오프셋 선택")
    print("2. 선택한 파일로 테스트 실행") 