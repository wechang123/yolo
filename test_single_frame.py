#!/usr/bin/env python3
"""
단일 프레임 테스트 스크립트
영상에서 특정 시간의 프레임을 추출하여 차량 인식 및 ROI 분석 테스트
"""

import cv2
import json
import numpy as np
from datetime import datetime
from parking_analysis_system import ParkingAnalysisSystem

def test_single_frame():
    """단일 프레임 테스트"""
    print("🔍 단일 프레임 테스트 시작")
    print("=" * 50)
    
    # 시스템 초기화 (백엔드 전송 비활성화)
    system = ParkingAnalysisSystem(
        video_path="IMG_8344.MOV",
        roi_path="roi_manual_coords.json",
        model_path="best_macos.pt",
        backend_url="http://localhost:8080",
        interval_minutes=3
    )
    
    # 테스트할 시간 (초 단위)
    test_times = [0, 180, 360, 540, 720]  # 0분, 3분, 6분, 9분, 12분
    
    for test_time in test_times:
        print(f"\n📸 테스트 시간: {test_time/60:.1f}분 ({test_time}초)")
        print("-" * 30)
        
        # 프레임 추출
        frame = system.extract_frame_at_time(test_time)
        if frame is None:
            print("❌ 프레임 추출 실패")
            continue
        
        print(f"✅ 프레임 추출 성공 - 크기: {frame.shape}")
        
        # 차량 탐지
        detections = system.detect_vehicles(frame)
        print(f"🚗 차량 탐지: {len(detections)}대")
        
        # 주차 슬롯 상태 확인
        slot_status = system.check_parking_slots(frame, detections)
        
        # 결과 출력
        available_slots = sum(1 for slot in slot_status if slot['is_available'])
        total_slots = len(slot_status)
        
        print(f"🅿️  주차 슬롯 상태: {available_slots}/{total_slots} 사용가능")
        
        # 상세 결과
        for slot in slot_status[:5]:  # 처음 5개 슬롯만 출력
            status = "사용가능" if slot['is_available'] else "사용중"
            print(f"  - {slot['slot_id']}: {status} (차량 {slot['vehicle_count']}대)")
        
        if len(slot_status) > 5:
            print(f"  ... 외 {len(slot_status) - 5}개 슬롯")
        
        # 결과 이미지 저장
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_image = frame.copy()
        
        # ROI 영역 그리기
        for slot in slot_status:
            roi_coords = slot['roi_coords']
            color = (0, 255, 0) if slot['is_available'] else (0, 0, 255)
            
            # 다각형 그리기
            pts = np.array(roi_coords, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(result_image, [pts], True, color, 2)
            
            # 슬롯 ID 표시
            center_x = sum(coord[0] for coord in roi_coords) // len(roi_coords)
            center_y = sum(coord[1] for coord in roi_coords) // len(roi_coords)
            cv2.putText(result_image, slot['slot_id'], (center_x-20, center_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # 차량 탐지 결과 그리기 (박스 크기 조정)
        for detection in detections:
            bbox = detection['bbox']
            conf = detection['confidence']
            # 박스 두께를 1로 줄이고, 더 정확한 박스 그리기
            cv2.rectangle(result_image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), 1)
            # confidence가 높은 것만 라벨 표시
            if conf > 0.3:
                cv2.putText(result_image, f"Car {conf:.2f}", (bbox[0], bbox[1]-5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
        
        # 결과 저장
        os.makedirs("test_results", exist_ok=True)
        cv2.imwrite(f"test_results/test_frame_{test_time}s.jpg", result_image)
        
        # JSON 결과 저장
        result_data = {
            'test_time_seconds': test_time,
            'test_time_minutes': test_time / 60,
            'timestamp': datetime.now().isoformat(),
            'vehicle_detections': len(detections),
            'slot_status': slot_status,
            'summary': {
                'total_slots': total_slots,
                'available_slots': available_slots,
                'occupied_slots': total_slots - available_slots,
                'occupancy_rate': (total_slots - available_slots) / total_slots * 100
            }
        }
        
        with open(f"test_results/test_result_{test_time}s.json", 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 결과 저장: test_results/test_frame_{test_time}s.jpg")
        print(f"📊 점유율: {result_data['summary']['occupancy_rate']:.1f}%")
    
    print("\n✅ 단일 프레임 테스트 완료!")
    print("📁 결과 파일들이 'test_results' 폴더에 저장되었습니다.")

if __name__ == "__main__":
    import os
    test_single_frame() 