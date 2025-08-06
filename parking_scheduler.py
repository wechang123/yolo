#!/usr/bin/env python3
"""
주차장 점유 현황 분석 스케줄러
3분마다 자동으로 차량 인식 및 점유 현황 분석을 실행
"""

import time
import schedule
import logging
from datetime import datetime
from parking_occupancy_analyzer import ParkingOccupancyAnalyzer
import subprocess
import os

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('parking_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ParkingScheduler:
    def __init__(self, 
                 video_path: str = "IMG_8344.MOV",
                 roi_path: str = "roi_full_rect_coords.json",
                 model_path: str = "best_macos.pt",
                 backend_url: str = "http://localhost:8080",
                 interval_minutes: int = 3):
        """
        주차장 분석 스케줄러 초기화
        
        Args:
            video_path: 분석할 영상 파일 경로
            roi_path: ROI 좌표 JSON 파일 경로
            model_path: YOLO 모델 파일 경로
            backend_url: 백엔드 서버 URL
            interval_minutes: 분석 간격 (분)
        """
        self.video_path = video_path
        self.roi_path = roi_path
        self.model_path = model_path
        self.backend_url = backend_url
        self.interval_minutes = interval_minutes
        
        # 분석기 초기화
        self.analyzer = ParkingOccupancyAnalyzer(
            roi_path=roi_path,
            model_path=model_path,
            backend_url=backend_url
        )
        
        logger.info(f"주차장 분석 스케줄러 초기화 완료 - {interval_minutes}분 간격")
    
    def extract_frame_from_video(self, target_minutes: int) -> str:
        """영상에서 특정 시간의 프레임 추출"""
        try:
            # 프레임 추출 명령어
            target_seconds = target_minutes * 60
            output_path = f"frame_{target_minutes}min.jpg"
            
            cmd = [
                "ffmpeg", "-i", self.video_path,
                "-ss", str(target_seconds),
                "-vframes", "1",
                "-q:v", "2",
                output_path,
                "-y"  # 기존 파일 덮어쓰기
            ]
            
            logger.info(f"프레임 추출: {target_minutes}분 지점")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"프레임 추출 완료: {output_path}")
                return output_path
            else:
                logger.error(f"프레임 추출 실패: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"프레임 추출 중 오류: {e}")
            return None
    
    def run_analysis_job(self):
        """분석 작업 실행"""
        try:
            logger.info("=== 주차장 점유 현황 분석 시작 ===")
            
            # 현재 시간을 기준으로 프레임 추출 (예: 30분, 33분, 36분...)
            current_time = datetime.now()
            minutes_from_start = (current_time.hour * 60 + current_time.minute) % self.interval_minutes
            
            # 프레임 추출
            frame_path = self.extract_frame_from_video(minutes_from_start)
            if not frame_path:
                logger.error("프레임 추출 실패")
                return
            
            # 분석기 업데이트
            self.analyzer.image_path = frame_path
            
            # 분석 실행
            self.analyzer.run_analysis()
            
            logger.info("=== 주차장 점유 현황 분석 완료 ===")
            
        except Exception as e:
            logger.error(f"분석 작업 실행 중 오류: {e}")
    
    def start_scheduler(self):
        """스케줄러 시작"""
        logger.info("주차장 분석 스케줄러 시작")
        
        # 3분마다 실행
        schedule.every(self.interval_minutes).minutes.do(self.run_analysis_job)
        
        # 즉시 첫 번째 실행
        logger.info("첫 번째 분석 작업 실행")
        self.run_analysis_job()
        
        # 스케줄러 루프
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 스케줄 확인
            except KeyboardInterrupt:
                logger.info("스케줄러 중단됨")
                break
            except Exception as e:
                logger.error(f"스케줄러 실행 중 오류: {e}")
                time.sleep(60)

def main():
    """메인 함수"""
    scheduler = ParkingScheduler()
    scheduler.start_scheduler()

if __name__ == "__main__":
    main() 