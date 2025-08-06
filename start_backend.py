#!/usr/bin/env python3
"""
DanParking 백엔드 서버 실행 스크립트
"""

import subprocess
import os
import time
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_backend_server():
    """백엔드 서버 시작"""
    try:
        # DanParking_BACKEND 디렉토리로 이동
        backend_dir = "DanParking_BACKEND"
        
        if not os.path.exists(backend_dir):
            logger.error(f"백엔드 디렉토리를 찾을 수 없습니다: {backend_dir}")
            return False
        
        os.chdir(backend_dir)
        logger.info(f"백엔드 디렉토리로 이동: {os.getcwd()}")
        
        # Gradle 빌드
        logger.info("Gradle 빌드 시작...")
        build_result = subprocess.run(["./gradlew", "build"], 
                                    capture_output=True, text=True)
        
        if build_result.returncode != 0:
            logger.error(f"빌드 실패: {build_result.stderr}")
            return False
        
        logger.info("빌드 성공!")
        
        # Spring Boot 서버 시작
        logger.info("Spring Boot 서버 시작...")
        server_process = subprocess.Popen(["./gradlew", "bootRun"], 
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        text=True)
        
        # 서버 시작 대기
        time.sleep(10)
        
        if server_process.poll() is None:
            logger.info("백엔드 서버가 성공적으로 시작되었습니다!")
            logger.info("서버 URL: http://localhost:8080")
            return server_process
        else:
            stdout, stderr = server_process.communicate()
            logger.error(f"서버 시작 실패: {stderr}")
            return False
            
    except Exception as e:
        logger.error(f"백엔드 서버 시작 중 오류: {e}")
        return False

def stop_backend_server(process):
    """백엔드 서버 중지"""
    if process:
        logger.info("백엔드 서버 중지 중...")
        process.terminate()
        process.wait()
        logger.info("백엔드 서버가 중지되었습니다.")

if __name__ == "__main__":
    print("🚗 DanParking 백엔드 서버 시작")
    print("=" * 50)
    
    server_process = start_backend_server()
    
    if server_process:
        try:
            print("\n서버가 실행 중입니다. Ctrl+C로 중지하세요.")
            server_process.wait()
        except KeyboardInterrupt:
            print("\n사용자에 의해 중지되었습니다.")
        finally:
            stop_backend_server(server_process)
    else:
        print("서버 시작에 실패했습니다.") 