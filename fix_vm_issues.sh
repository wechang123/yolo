#!/bin/bash
# VM 문제 해결 스크립트

echo "🔧 VM 문제 해결 시작..."

# 1. 패키지 업데이트
echo "📦 패키지 업데이트 중..."
pip install --upgrade pip
pip install --upgrade setuptools
pip install --upgrade pathlib2

# 2. Linux용 requirements 설치
echo "🐍 Linux용 패키지 설치 중..."
pip install -r requirements_linux.txt

# 3. 모델 변환
echo "🔄 모델 변환 중..."
python3 convert_model.py

# 4. 파일 권한 확인
echo "🔐 파일 권한 확인 중..."
chmod +x *.py
chmod +x *.sh

# 5. 환경 확인
echo "✅ 환경 확인 중..."
python3 -c "import torch; print(f'PyTorch 버전: {torch.__version__}')"
python3 -c "import cv2; print(f'OpenCV 버전: {cv2.__version__}')"
python3 -c "import shapely; print(f'Shapely 버전: {shapely.__version__}')"

echo "🎉 VM 문제 해결 완료!"
echo "이제 다음 명령어로 테스트하세요:"
echo "python3 parking_occupancy_analyzer.py"
