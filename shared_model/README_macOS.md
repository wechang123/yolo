# Campus Fine-tuned YOLOv5 Model - macOS 사용 가이드

## 📁 포함된 파일들

- `best.pt` - 학습된 최고 성능 모델 (14MB)
- `opt.yaml` - 학습 시 사용된 옵션 설정
- `hyp.yaml` - 하이퍼파라미터 설정
- `results.csv` - 학습 결과 데이터

## 🚀 macOS에서 사용하기

### 1. 환경 설정
```bash
# YOLOv5 리포지토리 클론 (맥에서)
git clone https://github.com/ultralytics/yolov5.git
cd yolov5

# 필요한 패키지 설치
pip install -r requirements.txt
```

### 2. 모델 파일 배치
```bash
# best.pt를 YOLOv5 루트 디렉토리에 복사
cp /path/to/best.pt ./
```

### 3. 추론 실행
```bash
# 이미지 추론
python detect.py --weights best.pt --source path/to/images

# 웹캠 실시간 추론
python detect.py --weights best.pt --source 0

# 동영상 추론
python detect.py --weights best.pt --source video.mp4

# 신뢰도 임계값 설정
python detect.py --weights best.pt --source images/ --conf 0.4
```

### 4. Python 코드에서 사용
```python
import torch
from models.experimental import attempt_load

# 모델 로드 (CPU - 안전한 방법)
model = attempt_load('best.pt', map_location='cpu')

# Apple Silicon Mac의 경우 MPS 사용 가능
# model = attempt_load('best.pt', map_location='mps')

# 추론 실행
results = model('path/to/image.jpg')
results.print()  # 결과 출력
results.save()   # 결과 저장
```

## 📊 모델 정보

- **학습 환경**: Windows 10
- **이미지 크기**: 1024x1024
- **배치 크기**: 16
- **에포크**: 50
- **옵티마이저**: SGD
- **학습률**: 0.01

## ⚠️ 주의사항

1. **플랫폼 호환성**: Windows에서 학습된 모델이지만 macOS에서 완벽 호환
2. **GPU 설정**: 
   - Intel Mac: CPU 사용 (`map_location='cpu'`)
   - Apple Silicon Mac: MPS 사용 가능 (`map_location='mps'`)
3. **메모리**: 14MB 모델이므로 메모리 부족 문제 없음

## 🔧 문제 해결

### CUDA 관련 오류 발생 시:
```python
# 강제로 CPU 사용
model = torch.load('best.pt', map_location='cpu')
```

### 버전 호환성 문제:
```bash
# PyTorch 재설치
pip install torch torchvision torchaudio
```

## 📈 성능 확인

`results.csv` 파일에서 학습 성능 지표를 확인할 수 있습니다:
- mAP@0.5
- mAP@0.5:0.95
- Precision
- Recall

Happy detecting! 🎯 