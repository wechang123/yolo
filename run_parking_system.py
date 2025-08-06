#!/usr/bin/env python3
"""
주차장 분석 시스템 통합 실행 스크립트
1. 백엔드 서버 시작
2. 영상 분석 및 데이터 전송
"""

import subprocess
import threading
import time
import logging
import os
from parking_analysis_system import ParkingAnalysisSystem

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ParkingSystemManager:
    def __init__(self):
        self.backend_process = None
        self.analysis_system = None
        
    def start_backend_server(self):
        """백엔드 서버를 별도 스레드에서 시작"""
        try:
            logger.info("백엔드 서버 시작 중...")
            
            # DanParking_BACKEND 디렉토리로 이동
            backend_dir = "DanParking_BACKEND"
            if not os.path.exists(backend_dir):
                logger.error(f"백엔드 디렉토리를 찾을 수 없습니다: {backend_dir}")
                return False
            
            # Gradle 빌드
            build_cmd = ["cd", backend_dir, "&&", "./gradlew", "build", "-q"]
            build_result = subprocess.run(" ".join(build_cmd), shell=True, capture_output=True)
            
            if build_result.returncode != 0:
                logger.error(f"빌드 실패: {build_result.stderr.decode()}")
                return False
            
            logger.info("빌드 성공!")
            
            # Spring Boot 서버 시작
            server_cmd = ["cd", backend_dir, "&&", "./gradlew", "bootRun"]
            self.backend_process = subprocess.Popen(
                " ".join(server_cmd), 
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 서버 시작 대기
            time.sleep(15)
            
            if self.backend_process.poll() is None:
                logger.info("✅ 백엔드 서버가 성공적으로 시작되었습니다!")
                logger.info("🌐 서버 URL: http://localhost:8080")
                return True
            else:
                stdout, stderr = self.backend_process.communicate()
                logger.error(f"❌ 서버 시작 실패: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"백엔드 서버 시작 중 오류: {e}")
            return False
    
    def start_analysis_system(self):
        """영상 분석 시스템 시작"""
        try:
            logger.info("영상 분석 시스템 시작 중...")
            
            # 분석 시스템 초기화
            self.analysis_system = ParkingAnalysisSystem(
                video_path="IMG_8344.MOV",
                roi_path="roi_full_rect_coords.json",
                model_path="best_macos.pt",
                backend_url="http://localhost:8080",
                interval_minutes=3
            )
            
            # 분석 실행
            self.analysis_system.run_analysis()
            
        except Exception as e:
            logger.error(f"영상 분석 시스템 실행 중 오류: {e}")
    
    def run_system(self):
        """전체 시스템 실행"""
        logger.info("🚗 주차장 분석 시스템 시작")
        logger.info("=" * 60)
        
        # 1. 백엔드 서버 시작
        backend_success = self.start_backend_server()
        if not backend_success:
            logger.error("백엔드 서버 시작 실패. 시스템을 종료합니다.")
            return
        
        # 2. 잠시 대기 후 분석 시스템 시작
        logger.info("백엔드 서버 안정화 대기 중...")
        time.sleep(5)
        
        # 3. 영상 분석 시스템 시작
        try:
            self.start_analysis_system()
        except KeyboardInterrupt:
            logger.info("사용자에 의해 분석이 중단되었습니다.")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """시스템 정리"""
        logger.info("시스템 정리 중...")
        
        if self.backend_process:
            logger.info("백엔드 서버 중지 중...")
            self.backend_process.terminate()
            self.backend_process.wait()
            logger.info("백엔드 서버가 중지되었습니다.")
        
        logger.info("시스템 정리 완료.")

def main():
    """메인 실행 함수"""
    print("🚗 단주차 주차장 분석 시스템")
    print("=" * 60)
    print("📋 실행할 작업:")
    print("1. DanParking 백엔드 서버 시작")
    print("2. 1시간 영상에서 3분마다 프레임 추출")
    print("3. YOLO 모델로 차량 인식")
    print("4. ROI 좌표와 비교하여 주차 슬롯 상태 분석")
    print("5. 백엔드 서버로 실시간 데이터 전송")
    print("=" * 60)
    
    # 사용자 확인
    response = input("시스템을 시작하시겠습니까? (y/N): ")
    if response.lower() != 'y':
        print("시스템 시작이 취소되었습니다.")
        return
    
    # 시스템 매니저 생성 및 실행
    manager = ParkingSystemManager()
    
    try:
        manager.run_system()
    except KeyboardInterrupt:
        print("\n사용자에 의해 시스템이 중단되었습니다.")
        manager.cleanup()
    except Exception as e:
        logger.error(f"시스템 실행 중 오류: {e}")
        manager.cleanup()

if __name__ == "__main__":
    main() 