#!/bin/bash

# 주차장 점유 현황 분석 시스템 시작 스크립트

echo "=== 주차장 점유 현황 분석 시스템 시작 ==="

# 1. 가상환경 활성화
echo "가상환경 활성화 중..."
source yolo_env/bin/activate

# 2. 필요한 파일 확인
echo "필요한 파일 확인 중..."
required_files=("best_macos.pt" "frame_30min.jpg" "roi_full_rect_coords.json" "detect.py")

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "오류: 필요한 파일이 없습니다: $file"
        exit 1
    fi
done

echo "모든 필요한 파일 확인 완료"

# 3. 백엔드 서버 상태 확인
echo "백엔드 서버 상태 확인 중..."
if curl -s http://localhost:8080/parking-lots > /dev/null 2>&1; then
    echo "백엔드 서버가 실행 중입니다."
else
    echo "백엔드 서버가 실행되지 않았습니다. 백그라운드에서 시작합니다..."
    cd DanParking_BACKEND
    nohup ./gradlew bootRun > ../backend.log 2>&1 &
    cd ..
    sleep 30  # 서버 시작 대기
fi

# 4. 단일 분석 실행 (테스트)
echo "단일 분석 실행 (테스트)..."
python3 parking_occupancy_analyzer.py

# 5. 스케줄러 시작 여부 확인
echo ""
echo "스케줄러를 시작하시겠습니까? (y/n)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "3분마다 자동 분석 스케줄러 시작..."
    python3 parking_scheduler.py
else
    echo "스케줄러를 시작하지 않습니다."
    echo "수동으로 실행하려면: python3 parking_occupancy_analyzer.py"
fi

echo "=== 주차장 점유 현황 분석 시스템 종료 ===" 