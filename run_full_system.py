#!/usr/bin/env python3
"""
전체 주차장 분석 시스템 실행 (백엔드 없이 분석만)
1시간 영상에서 3분마다 프레임 추출 → YOLO 차량 인식 → ROI 비교 → 결과 저장
"""

import os
import time
import logging
from datetime import datetime
from parking_analysis_system import ParkingAnalysisSystem

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('full_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_full_analysis():
    """전체 영상 분석 실행"""
    print("🚗 주차장 영상 전체 분석 시스템")
    print("=" * 60)
    print("📋 실행할 작업:")
    print("1. 1시간 영상에서 3분마다 프레임 추출")
    print("2. YOLO 모델로 차량 인식")
    print("3. ROI 좌표와 비교하여 주차 슬롯 상태 분석")
    print("4. 결과 이미지와 JSON 데이터 저장")
    print("=" * 60)
    
    # 사용자 확인
    response = input("전체 분석을 시작하시겠습니까? (y/N): ")
    if response.lower() != 'y':
        print("분석이 취소되었습니다.")
        return
    
    try:
        # 분석 시스템 초기화
        logger.info("분석 시스템 초기화 중...")
        system = ParkingAnalysisSystem(
            video_path="IMG_8344.MOV",
            roi_path="roi_precise_offset_150.json",
            model_path="best_macos.pt",
            backend_url="http://localhost:8080",  # 백엔드 전송 비활성화
            interval_minutes=3
        )
        
        # 결과 저장 디렉토리 생성
        os.makedirs("full_analysis_results", exist_ok=True)
        
        logger.info("전체 영상 분석 시작")
        start_time = time.time()
        
        # 영상 시작부터 끝까지 3분 간격으로 분석
        current_time = 0.0
        analysis_count = 0
        total_vehicles = 0
        
        while current_time <= system.video_info['duration_seconds']:
            logger.info(f"분석 진행률: {current_time/system.video_info['duration_seconds']*100:.1f}%")
            
            # 현재 시간에 해당하는 프레임 추출
            frame = system.extract_frame_at_time(current_time)
            if frame is None:
                current_time += system.interval_seconds
                continue
            
            # 차량 탐지
            detections = system.detect_vehicles(frame)
            total_vehicles += len(detections)
            
            # 주차 슬롯 상태 확인
            slot_status = system.check_parking_slots(frame, detections)
            
            # 현재 시간 계산
            timestamp = datetime.now()
            
            # 결과 저장
            system.save_analysis_result(slot_status, timestamp, frame)
            
            # 통계 출력
            available_slots = sum(1 for s in slot_status if s['is_available'])
            total_slots = len(slot_status)
            occupancy_rate = (total_slots - available_slots) / total_slots * 100
            
            analysis_count += 1
            logger.info(f"분석 완료 #{analysis_count} - 시간: {current_time/60:.1f}분")
            logger.info(f"  🚗 차량: {len(detections)}대 탐지")
            logger.info(f"  🅿️  슬롯: {available_slots}/{total_slots} 사용가능 ({occupancy_rate:.1f}% 점유)")
            
            # 다음 분석 시간으로 이동
            current_time += system.interval_seconds
        
        # 최종 통계
        end_time = time.time()
        total_duration = end_time - start_time
        
        logger.info("=" * 60)
        logger.info("🎉 전체 분석 완료!")
        logger.info(f"📊 최종 통계:")
        logger.info(f"  • 총 분석 횟수: {analysis_count}회")
        logger.info(f"  • 총 탐지 차량: {total_vehicles}대")
        logger.info(f"  • 평균 차량/분석: {total_vehicles/analysis_count:.1f}대")
        logger.info(f"  • 총 소요 시간: {total_duration/60:.1f}분")
        logger.info(f"  • 평균 처리 시간: {total_duration/analysis_count:.1f}초/분석")
        logger.info(f"📁 결과 저장: full_analysis_results/")
        
        print("\n✅ 전체 분석이 성공적으로 완료되었습니다!")
        print(f"📊 총 {analysis_count}회 분석, {total_vehicles}대 차량 탐지")
        print(f"📁 결과 파일들이 'full_analysis_results' 폴더에 저장되었습니다.")
        
    except KeyboardInterrupt:
        logger.info("사용자에 의해 분석이 중단되었습니다.")
        print("\n⚠️ 분석이 중단되었습니다.")
    except Exception as e:
        logger.error(f"분석 중 오류 발생: {e}")
        print(f"\n❌ 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    run_full_analysis() 