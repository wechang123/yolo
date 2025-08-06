# 주차장 점유 현황 분석 시스템

YOLO 차량 인식을 통해 주차장의 점유 현황을 실시간으로 분석하고 백엔드 서버로 전송하는 시스템입니다.

## 주요 기능

- **차량 인식**: YOLO 모델을 사용한 최대한의 차량 인식 (conf: 0.0399)
- **ROI 기반 분석**: 주차 슬롯별 ROI 좌표와 차량 위치 비교
- **점유율 계산**: 전체 슬롯 대비 점유 슬롯 비율 계산 (예: 70/30)
- **자동 전송**: 3분마다 백엔드 서버로 JSON 형태로 데이터 전송
- **정확한 분석**: 주차장이 아닌 차량은 점유율에 반영되지 않음

## 시스템 구조

```
parking_occupancy_analyzer.py  # 메인 분석기
parking_scheduler.py           # 3분마다 자동 실행 스케줄러
run_parking_analysis.py        # 수동 실행 스크립트
DanParking_BACKEND/           # 백엔드 서버 (Spring Boot)
```

## 설치 및 설정

### 1. 가상환경 활성화
```bash
source yolo_env/bin/activate
```

### 2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. 백엔드 서버 실행
```bash
cd DanParking_BACKEND
./gradlew bootRun
```

## 사용법

### 1. 단일 이미지 분석
```bash
# 가상환경 활성화 후
python3 parking_occupancy_analyzer.py
```

### 2. YOLO 인식만 실행
```bash
python3 detect.py --weights best_macos.pt --source frame_30min.jpg --conf 0.0399 --iou 0.0 --save-txt
```

### 3. 전체 시스템 실행 (수동)
```bash
python3 run_parking_analysis.py
```

### 4. 자동 스케줄러 실행 (3분마다)
```bash
python3 parking_scheduler.py
```

## 데이터 형식

### 백엔드로 전송되는 JSON 형식
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "parking_lot_id": "sanggyeonggwan",
  "occupancy_info": {
    "total_slots": 100,
    "occupied_slots": 70,
    "total_vehicles": 70,
    "occupancy_rate": 70.0,
    "occupancy_ratio": "70/100"
  },
  "slot_details": [
    {
      "slot_id": "slot_1",
      "occupied": true,
      "vehicle_count": 1
    },
    {
      "slot_id": "slot_2",
      "occupied": false,
      "vehicle_count": 0
    }
  ]
}
```

## API 엔드포인트

### 점유 현황 업데이트
```
POST /parking-lots/occupancy
Authorization: Bearer yolo_token
Content-Type: application/json
```

### 점유 현황 조회
```
GET /parking-lots/occupancy/{parkingLotId}
```

## 설정 파일

### ROI 좌표 파일
- `roi_full_rect_coords.json`: 주차 슬롯별 ROI 좌표
- 각 슬롯의 다각형 좌표로 주차 공간 정의

### YOLO 모델
- `best_macos.pt`: 훈련된 차량 인식 모델
- conf: 0.0399, iou: 0.0으로 최대한의 차량 인식

## 로그 파일

- `parking_occupancy.log`: 분석기 로그
- `parking_scheduler.log`: 스케줄러 로그
- `run_analysis.log`: 실행 스크립트 로그

## 분석 결과

### 점유율 계산 방식
- **전체 슬롯**: ROI로 정의된 주차 공간 수
- **점유 슬롯**: 차량이 감지된 슬롯 수
- **점유율**: (점유 슬롯 / 전체 슬롯) × 100
- **점유 비율**: "점유 슬롯/전체 슬롯" 형태

### 차량 인식 기준
- 차량 클래스 ID: 0(car), 2(car), 3(motorcycle), 5(bus), 7(truck)
- 바운딩 박스 중심점이 ROI 내부에 있을 때 점유로 판단
- 주차장 외부 차량은 점유율에 반영되지 않음

## 문제 해결

### 1. YOLO 인식 실패
- 모델 파일 경로 확인: `best_macos.pt`
- 이미지 파일 존재 확인: `frame_30min.jpg`
- 가상환경 활성화 확인

### 2. 백엔드 연결 실패
- 백엔드 서버 실행 상태 확인
- 포트 8080 접근 가능 여부 확인
- JWT 토큰 설정 확인

### 3. ROI 좌표 오류
- `roi_full_rect_coords.json` 파일 형식 확인
- 좌표값이 이미지 크기 내에 있는지 확인

## 성능 최적화

- **GPU 사용**: MPS (Apple Silicon) 또는 CUDA 사용
- **배치 처리**: 여러 이미지 동시 처리 가능
- **메모리 관리**: 분석 후 메모리 정리

## 모니터링

- 실시간 로그 확인
- 점유율 변화 추이 모니터링
- 백엔드 전송 성공률 확인 