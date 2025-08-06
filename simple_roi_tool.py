#!/usr/bin/env python3
"""
매우 간단한 ROI 좌표 찍기 도구
확대/축소가 확실히 작동하는 버전
"""

import cv2
import numpy as np
import json
import os

def main():
    # 이미지 로드
    image_path = "frame_30min.jpg"
    if not os.path.exists(image_path):
        print(f"❌ 이미지 파일을 찾을 수 없습니다: {image_path}")
        return
    
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ 이미지를 읽을 수 없습니다: {image_path}")
        return
    
    print(f"✅ 이미지 로드 완료: {image_path}")
    print(f"   크기: {image.shape[1]}×{image.shape[0]}")
    
    # 변수 초기화
    scale = 1.0
    points = []
    rectangles = []
    
    def mouse_callback(event, x, y, flags, param):
        nonlocal points, rectangles
        
        # 좌표 변환
        real_x = int(x / scale)
        real_y = int(y / scale)
        
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(points) < 4:
                points.append([real_x, real_y])
                print(f"✅ 점 {len(points)} 추가: ({real_x}, {real_y})")
                
                if len(points) == 4:
                    # 사각형 생성
                    center_x = sum(p[0] for p in points) / 4
                    center_y = sum(p[1] for p in points) / 4
                    
                    angles = []
                    for point in points:
                        angle = np.arctan2(point[1] - center_y, point[0] - center_x)
                        angles.append(angle)
                    
                    sorted_points = [p for _, p in sorted(zip(angles, points))]
                    
                    rectangles.append({
                        'points': sorted_points,
                        'slot_id': f'slot_{len(rectangles) + 1}'
                    })
                    
                    print(f"✅ 사각형 {len(rectangles)} 생성 완료")
                    points = []
        
        elif event == cv2.EVENT_RBUTTONDOWN:
            if points:
                removed_point = points.pop()
                print(f"❌ 점 {len(points) + 1} 삭제")
    
    # 창 생성
    window_name = "ROI 좌표 찍기"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_name, mouse_callback)
    
    print("\n🎯 ROI 좌표 찍기 도구")
    print("=" * 30)
    print("마우스:")
    print("  • 좌클릭: 점 추가 (4개까지)")
    print("  • 우클릭: 점 삭제")
    print("키보드:")
    print("  • + / -: 확대/축소")
    print("  • R: 모든 점 삭제")
    print("  • S: 저장")
    print("  • Q: 종료")
    
    while True:
        # 이미지 복사 및 확대/축소
        display_image = image.copy()
        height, width = image.shape[:2]
        new_width = int(width * scale)
        new_height = int(height * scale)
        display_image = cv2.resize(display_image, (new_width, new_height))
        
        # 점 그리기
        for i, point in enumerate(points):
            x, y = point
            display_x = int(x * scale)
            display_y = int(y * scale)
            
            if (0 <= display_x < new_width and 0 <= display_y < new_height):
                cv2.circle(display_image, (display_x, display_y), 5, (0, 255, 0), -1)
                cv2.circle(display_image, (display_x, display_y), 7, (255, 255, 255), 2)
                cv2.putText(display_image, str(i+1), (display_x+10, display_y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 사각형 그리기
        for rect in rectangles:
            points_rect = rect['points']
            slot_id = rect['slot_id']
            
            display_points = []
            for point in points_rect:
                x, y = point
                display_x = int(x * scale)
                display_y = int(y * scale)
                display_points.append([display_x, display_y])
            
            pts = np.array(display_points, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(display_image, [pts], True, (0, 255, 0), 2)
            
            center_x = sum(p[0] for p in display_points) // 4
            center_y = sum(p[1] for p in display_points) // 4
            cv2.putText(display_image, slot_id, (center_x-20, center_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # 정보 표시
        info_text = f"점: {len(points)}/4 | 사각형: {len(rectangles)} | 확대: {scale:.1f}x"
        cv2.putText(display_image, info_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 창 크기 조정
        cv2.resizeWindow(window_name, new_width, new_height)
        cv2.imshow(window_name, display_image)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('+') or key == ord('='):
            scale = min(5.0, scale + 0.2)
            print(f"🔍 확대: {scale:.1f}x")
        elif key == ord('-'):
            scale = max(0.1, scale - 0.2)
            print(f"🔍 축소: {scale:.1f}x")
        elif key == ord('r'):
            points = []
            rectangles = []
            print("🔄 모든 점과 사각형 삭제")
        elif key == ord('s'):
            if rectangles:
                # JSON 저장
                roi_data = {
                    "frame_30min.jpg": []
                }
                
                for rect in rectangles:
                    roi_data["frame_30min.jpg"].append({
                        "slot_id": rect['slot_id'],
                        "coords": rect['points']
                    })
                
                output_path = "roi_manual_coords.json"
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(roi_data, f, ensure_ascii=False, indent=4)
                
                print(f"✅ ROI 좌표 저장 완료: {output_path}")
                print(f"   총 {len(rectangles)}개 사각형")
                
                # 미리보기 생성
                preview_image = image.copy()
                for rect in rectangles:
                    points_rect = rect['points']
                    slot_id = rect['slot_id']
                    
                    pts = np.array(points_rect, np.int32)
                    pts = pts.reshape((-1, 1, 2))
                    cv2.polylines(preview_image, [pts], True, (0, 255, 0), 2)
                    
                    center_x = sum(p[0] for p in points_rect) // 4
                    center_y = sum(p[1] for p in points_rect) // 4
                    cv2.putText(preview_image, slot_id, (center_x-20, center_y), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                cv2.imwrite("roi_manual_preview.jpg", preview_image)
                print(f"✅ 미리보기 저장: roi_manual_preview.jpg")
            else:
                print("❌ 저장할 사각형이 없습니다.")
    
    cv2.destroyAllWindows()
    print("\n✅ ROI 좌표 찍기 완료!")

if __name__ == "__main__":
    main() 