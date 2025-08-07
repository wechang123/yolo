# 주차장 점유 현황 시각화 도구

주차장 점유 현황을 시각화하고 IoU 임계값을 조정할 수 있는 도구입니다.

## 🎨 시각화 기능

- **초록색**: 비어있는 주차 슬롯
- **빨간색**: 점유된 주차 슬롯
- **파란색**: 감지된 차량 바운딩 박스
- **IoU 값**: 각 슬롯의 최대 IoU 값 표시

## 🚀 사용법

### 1. 기본 시각화 (IoU 0.1)
```bash
source yolo_env/bin/activate
python3 visualize_occupancy.py --iou 0.1 --output occupancy_visualization_iou0.10.jpg
```

### 2. 다른 IoU 값으로 시각화
```bash
# IoU 0.05 (더 관대한 판단)
python3 visualize_occupancy.py --iou 0.05 --output occupancy_visualization_iou0.05.jpg

# IoU 0.15 (더 엄격한 판단)
python3 visualize_occupancy.py --iou 0.15 --output occupancy_visualization_iou0.15.jpg
```

### 3. 차량 바운딩 박스 숨기기
```bash
python3 visualize_occupancy.py --iou 0.1 --no-vehicles --output occupancy_clean.jpg
```

### 4. 최적 IoU 임계값 찾기
```bash
python3 visualize_occupancy.py --find-optimal
```

## 📊 IoU 임계값별 결과 분석

### 현재 데이터 기준 결과:
- **IoU 0.01-0.02**: 19/79 (24.1%) - 가장 관대
- **IoU 0.03-0.04**: 18/79 (22.8%)
- **IoU 0.05**: 17/79 (21.5%)
- **IoU 0.06-0.08**: 14/79 (17.7%)
- **IoU 0.09-0.10**: 13/79 (16.5%) - 현재 설정
- **IoU 0.11-0.13**: 12/79 (15.2%)
- **IoU 0.14-0.16**: 10/79 (12.7%)
- **IoU 0.17**: 8/79 (10.1%)
- **IoU 0.18-0.19**: 7/79 (8.9%)
- **IoU 0.20**: 5/79 (6.3%)
- **IoU 0.21**: 4/79 (5.1%)
- **IoU 0.22**: 3/79 (3.8%)
- **IoU 0.23-0.24**: 1/79 (1.3%)
- **IoU 0.25+**: 0/79 (0.0%) - 가장 엄격

## 🎯 권장 IoU 임계값

### 상황별 권장값:
- **관대한 판단**: IoU 0.05-0.08 (17-14개 슬롯)
- **균형잡힌 판단**: IoU 0.09-0.12 (13-12개 슬롯) ⭐ **권장**
- **엄격한 판단**: IoU 0.13-0.16 (12-10개 슬롯)
- **매우 엄격한 판단**: IoU 0.17+ (8개 이하 슬롯)

## 📁 생성된 파일들

### 시각화 이미지
- `occupancy_visualization_iou0.05.jpg` - IoU 0.05 시각화
- `occupancy_visualization_iou0.10.jpg` - IoU 0.10 시각화
- `occupancy_visualization_iou0.15.jpg` - IoU 0.15 시각화

### 로그 파일
- `visualize_occupancy.log` - 시각화 과정 로그

## 🔧 명령어 옵션

```bash
python3 visualize_occupancy.py [옵션]

옵션:
  --iou FLOAT           IoU 임계값 (기본값: 0.1)
  --no-vehicles         차량 바운딩 박스 숨기기
  --output PATH         출력 이미지 경로
  --find-optimal        최적 IoU 임계값 찾기
  --target-occupancy    목표 점유율 (%)
```

## 📈 시각화 예시

### IoU 0.05 (21.5% 점유율)
- 더 많은 슬롯이 점유로 판단됨
- 약간의 겹침만 있어도 점유로 인식

### IoU 0.10 (16.5% 점유율) - 현재 설정
- 균형잡힌 판단
- 적절한 겹침이 있을 때만 점유로 인식

### IoU 0.15 (12.7% 점유율)
- 더 엄격한 판단
- 상당한 겹침이 있을 때만 점유로 인식

## 🎨 시각화 요소

### 색상 코드
- **초록색 (0, 255, 0)**: 비어있는 슬롯
- **빨간색 (0, 0, 255)**: 점유된 슬롯
- **파란색 (255, 0, 0)**: 차량 바운딩 박스
- **노란색 (0, 255, 255)**: 텍스트

### 표시 정보
- 슬롯 ID (예: slot_3)
- 최대 IoU 값 (예: IoU:0.244)
- 전체 점유율 통계
- IoU 임계값
- 범례

## 🔍 분석 팁

1. **IoU 값 확인**: 각 슬롯의 IoU 값을 확인하여 적절한 임계값 설정
2. **차량 위치 확인**: 파란색 바운딩 박스로 차량 위치 확인
3. **점유율 조정**: 목표 점유율에 맞게 IoU 임계값 조정
4. **시각적 검증**: 실제 이미지와 비교하여 정확성 검증

## 🚀 빠른 시작

```bash
# 1. 최적 IoU 값 찾기
python3 visualize_occupancy.py --find-optimal

# 2. 권장 IoU 값으로 시각화
python3 visualize_occupancy.py --iou 0.1 --output my_visualization.jpg

# 3. 결과 확인
open my_visualization.jpg
```
