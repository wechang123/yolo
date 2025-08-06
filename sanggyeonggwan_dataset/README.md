# 상경관(Sanggyeonggwan) YOLOv5 데이터셋

## 📖 개요
상경관 건물 내부에서 촬영된 이미지와 객체 탐지 라벨 데이터셋입니다.

## 📁 데이터셋 구조
```
sanggyeonggwan_dataset/
├── images/          # 원본 이미지 파일들
│   ├── Sanggyeonggwan_c1_1.jpeg
│   ├── Sanggyeonggwan_c1_2.JPG
│   ├── ...
├── labels/          # YOLO 형식 라벨 파일들
│   ├── Sanggyeonggwan_c1_1.txt
│   ├── Sanggyeonggwan_c1_2.txt
│   ├── ...
│   └── classes.txt  # 클래스 정보
└── README.md        # 이 파일
```

## 📊 데이터셋 정보

### 이미지 정보
- **총 이미지 수**: 13장
- **파일 형식**: JPEG, JPG
- **해상도**: 다양한 크기 (약 3-8MB per image)
- **촬영 위치**: 상경관 내부 여러 층

### 클래스 정보
상세한 클래스는 `labels/classes.txt` 파일을 참조하세요.

### 파일 명명 규칙
- `Sanggyeonggwan_c[카메라번호]_[이미지번호].[확장자]`
- 예: `Sanggyeonggwan_c1_1.jpeg` (1번 카메라, 1번째 이미지)

## 🚀 사용 방법

### 1. YOLOv5와 함께 사용하기
```bash
# YOLOv5 디렉토리에 복사
cp -r sanggyeonggwan_dataset /path/to/yolov5/

# 데이터셋 YAML 파일 생성 필요
```

### 2. 학습용 데이터 YAML 생성 예시
```yaml
# sanggyeonggwan.yaml
path: sanggyeonggwan_dataset
train: images
val: images  # 또는 별도 검증 세트 지정

# Classes (classes.txt 내용에 맞게 수정)
names:
  0: person
  1: object
  # 실제 클래스는 classes.txt 참조
```

### 3. YOLOv5 학습 실행 예시
```bash
python train.py --data sanggyeonggwan.yaml --weights yolov5s.pt --epochs 100
```

## 📈 데이터셋 활용

### 전이 학습 (Transfer Learning)
- 기존 학습된 모델에서 상경관 특화 fine-tuning
- 적은 데이터로도 효과적인 학습 가능

### 객체 탐지 성능 향상
- 상경관 환경에 특화된 모델 개발
- 실내 환경에서의 객체 탐지 정확도 개선

## 📝 라이선스 및 사용 조건
- 연구 및 교육 목적으로 사용
- 상업적 이용 시 별도 문의

## 🔗 관련 자료
- [YOLOv5 공식 저장소](https://github.com/ultralytics/yolov5)
- [YOLO 라벨 형식 가이드](https://docs.ultralytics.com/datasets/)

## 📞 문의
데이터셋 관련 문의사항이 있으시면 GitHub Issues를 통해 연락주세요.

---
**Created**: 2025년 8월  
**Last Updated**: 2025년 8월 