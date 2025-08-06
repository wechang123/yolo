#!/usr/bin/env python3
"""
주차장 점유 현황 분석 스케줄러 테스트 버전
1분마다 실행하여 테스트
"""

import time
import schedule
import logging
from datetime import datetime
from parking_occupancy_analyzer import ParkingOccupancyAnalyzer

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_test_analysis():
    """테스트 분석 작업 실행"""
    try:
        logger.info("=== 테스트 분석 작업 시작 ===")
        
        # 분석기 초기화
        analyzer = ParkingOccupancyAnalyzer()
        
        # 분석 실행
        analyzer.run_analysis()
        
        logger.info("=== 테스트 분석 작업 완료 ===")
        
    except Exception as e:
        logger.error(f"테스트 분석 작업 실행 중 오류: {e}")

def main():
    """메인 함수"""
    logger.info("테스트 스케줄러 시작 (1분 간격)")
    
    # 1분마다 실행 (테스트용)
    schedule.every(1).minutes.do(run_test_analysis)
    
    # 즉시 첫 번째 실행
    logger.info("첫 번째 테스트 분석 작업 실행")
    run_test_analysis()
    
    # 스케줄러 루프 (5분간 실행)
    start_time = time.time()
    while time.time() - start_time < 300:  # 5분간 실행
        try:
            schedule.run_pending()
            time.sleep(10)  # 10초마다 스케줄 확인
        except KeyboardInterrupt:
            logger.info("테스트 스케줄러 중단됨")
            break
        except Exception as e:
            logger.error(f"테스트 스케줄러 실행 중 오류: {e}")
            time.sleep(10)
    
    logger.info("테스트 스케줄러 종료")

if __name__ == "__main__":
    main() 