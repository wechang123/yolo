# 맥OS에서 YOLOv5 모델 사용하기 - 완전 가이드

## 🚀 처음부터 끝까지 단계별 가이드

### 1단계: 필요한 도구 설치

#### 1.1 Homebrew 설치 (패키지 매니저)
```bash
# Terminal 열기 (Cmd + Space → "Terminal" 검색)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 1.2 Python 설치
```bash
# Python 3.8 이상 설치
brew install python@3.9

# Python 버전 확인
python3 --version
```

#### 1.3 Git 확인 (보통 이미 설치되어 있음)
```bash
git --version
# 없다면: brew install git
```

### 2단계: 새로운 프로젝트 디렉토리 생성

#### 2.1 작업 디렉토리 만들기
```bash
# 홈 디렉토리로 이동
cd ~

# 새 프로젝트 폴더 생성
mkdir yolo_project
cd yolo_project

# 현재 위치 확인
pwd
# 출력: /Users/[사용자명]/yolo_project
```

### 3단계: YOLOv5 리포지토리 클론

#### 3.1 공식 YOLOv5 다운로드
```bash
# GitHub에서 YOLOv5 클론
git clone https://github.com/ultralytics/yolov5.git

# YOLOv5 디렉토리로 이동
cd yolov5

# 디렉토리 구조 확인
ls -la
```

#### 3.2 Python 가상환경 생성 (권장)
```bash
# 가상환경 생성
python3 -m venv yolo_env

# 가상환경 활성화
source yolo_env/bin/activate

# 프롬프트가 (yolo_env)로 시작하면 성공
```

### 4단계: 필요한 패키지 설치

#### 4.1 PyTorch 및 의존성 설치
```bash
# 필수 패키지 설치
pip install --upgrade pip

# YOLOv5 요구사항 설치
pip install -r requirements.txt

# PyTorch 설치 확인
python3 -c "import torch; print(f'PyTorch 버전: {torch.__version__}')"
```

#### 4.2 Apple Silicon Mac의 경우 (M1/M2/M3)
```bash
# MPS(Metal Performance Shaders) 지원 확인
python3 -c "import torch; print(f'MPS 사용 가능: {torch.backends.mps.is_available()}')"
```

### 5단계: 학습된 모델 파일 추가

#### 5.1 모델 파일 복사
```bash
# campus_model.zip을 Downloads에서 복사했다고 가정
cd ~/yolo_project/yolov5

# zip 파일 압축 해제 (Finder에서 더블클릭으로도 가능)
unzip ~/Downloads/campus_model.zip

# 모델 파일을 YOLOv5 루트로 복사
cp campus_model/best.pt ./

# 파일 복사 확인
ls -la *.pt
```

#### 5.2 모델 정보 확인
```bash
# 모델 정보 확인 스크립트 실행
python3 -c "
import torch
model = torch.load('best.pt', map_location='cpu')
print('=== 모델 정보 ===')
print(f'모델 크기: {len(str(model))/1024/1024:.1f}MB')
print(f'사용 가능한 키: {list(model.keys())[:5]}')
print('모델 로드 성공!')
"
```

### 6단계: 첫 번째 추론 실행

#### 6.1 기본 이미지로 테스트
```bash
# YOLOv5에 포함된 샘플 이미지로 테스트
python3 detect.py --weights best.pt --source data/images/bus.jpg

# 결과 확인
open runs/detect/exp/bus.jpg
```

#### 6.2 웹캠으로 실시간 테스트
```bash
# 웹캠 실시간 추론 (0번 카메라)
python3 detect.py --weights best.pt --source 0 --view-img

# 종료: 'q' 키 또는 Ctrl+C
```

### 7단계: 새로운 이미지/비디오로 테스트

#### 7.1 테스트 이미지 폴더 생성
```bash
# 테스트용 이미지 폴더 생성
mkdir test_images
cd test_images

# 이곳에 테스트할 이미지들을 복사
# Finder에서 드래그&드롭으로 이미지 추가
```

#### 7.2 여러 이미지 한번에 처리
```bash
# 돌아가서 추론 실행
cd ..
python3 detect.py --weights best.pt --source test_images/ --save-txt --save-conf

# 결과 폴더 열기
open runs/detect/exp2/
```

### 8단계: 고급 사용법

#### 8.1 신뢰도 임계값 조정
```bash
# 신뢰도 40% 이상만 탐지
python3 detect.py --weights best.pt --source test_images/ --conf 0.4

# 신뢰도 60% 이상만 탐지
python3 detect.py --weights best.pt --source test_images/ --conf 0.6
```

#### 8.2 특정 클래스만 탐지
```bash
# 클래스 0번과 2번만 탐지 (classes.txt 참고)
python3 detect.py --weights best.pt --source test_images/ --classes 0 2
```

#### 8.3 결과 저장 위치 지정
```bash
# 결과를 특정 폴더에 저장
python3 detect.py --weights best.pt --source test_images/ --project my_results --name test1
```

### 9단계: Python 코드로 사용하기

#### 9.1 간단한 Python 스크립트 생성
```bash
# 새 Python 파일 생성
nano my_detection.py
```

```python
# my_detection.py 내용
import torch
from models.experimental import attempt_load
from utils.general import non_max_suppression, scale_coords
from utils.plots import plot_one_box
import cv2
import numpy as np

def load_model():
    """모델 로드"""
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    print(f"사용 장치: {device}")
    
    model = attempt_load('best.pt', map_location=device)
    model.eval()
    return model, device

def detect_image(model, device, image_path):
    """이미지에서 객체 탐지"""
    # 이미지 로드
    img = cv2.imread(image_path)
    if img is None:
        print(f"이미지를 찾을 수 없습니다: {image_path}")
        return
    
    # 추론 실행
    results = model(img)
    
    # 결과 출력
    results.print()
    results.save()
    
    print(f"결과가 runs/detect/exp/ 폴더에 저장되었습니다.")

if __name__ == "__main__":
    # 모델 로드
    model, device = load_model()
    
    # 이미지 탐지 실행
    detect_image(model, device, "data/images/bus.jpg")
```

#### 9.2 스크립트 실행
```bash
# Python 스크립트 실행
python3 my_detection.py
```

### 10단계: 문제 해결

#### 10.1 일반적인 오류들

**CUDA 오류 발생 시:**
```bash
# 강제로 CPU 사용
export CUDA_VISIBLE_DEVICES=""
python3 detect.py --weights best.pt --source test_images/ --device cpu
```

**메모리 부족 오류:**
```bash
# 배치 크기 줄이기
python3 detect.py --weights best.pt --source test_images/ --batch-size 1
```

**권한 오류:**
```bash
# 실행 권한 추가
chmod +x detect.py
```

#### 10.2 성능 최적화 (Apple Silicon)
```bash
# MPS 백엔드 사용 (M1/M2/M3 Mac)
python3 detect.py --weights best.pt --source test_images/ --device mps
```

### 11단계: 결과 확인 및 분석

#### 11.1 결과 폴더 구조
```
runs/detect/exp/
├── bus.jpg          # 탐지 결과 이미지
├── labels/           # 탐지된 객체 좌표 (txt)
└── crops/           # 탐지된 객체만 잘라낸 이미지
```

#### 11.2 성능 지표 확인
```bash
# campus_model 폴더의 results.csv 파일 열기
open campus_model/results.csv

# 또는 터미널에서 확인
cat campus_model/results.csv
```

### 🎯 완료!

이제 맥OS에서 윈도우에서 학습한 YOLOv5 모델을 성공적으로 사용할 수 있습니다!

### 📞 추가 도움말

- **YOLOv5 공식 문서**: https://docs.ultralytics.com/
- **PyTorch 공식 사이트**: https://pytorch.org/
- **문제 발생 시**: GitHub Issues에서 검색

### 🔄 가상환경 관리

```bash
# 가상환경 비활성화
deactivate

# 다음에 다시 사용할 때
cd ~/yolo_project/yolov5
source yolo_env/bin/activate
```

**Happy Detecting on macOS! 🍎🎯** 