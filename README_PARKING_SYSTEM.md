# 🚗 주차장 영상 분석 및 백엔드 전송 시스템

1시간짜리 주차장 영상에서 3분마다 프레임을 추출하고, YOLO 모델로 차량을 인식한 후 ROI 좌표와 비교하여 주차장 현황을 백엔드 서버로 전송하는 시스템입니다.

## 📋 시스템 구성

### 🔧 주요 컴포넌트
- **영상 처리**: OpenCV를 사용한 프레임 추출
- **차량 인식**: YOLOv5 모델 (`best_macos.pt`)
- **ROI 분석**: 주차 슬롯 좌표와 차량 위치 비교
- **백엔드 연동**: DanParking Spring Boot 서버
- **데이터 전송**: REST API를 통한 실시간 상태 업데이트

### 📁 파일 구조
```
yolo/
├── parking_analysis_system.py      # 메인 분석 시스템
├── run_parking_system.py           # 통합 실행 스크립트
├── test_single_frame.py            # 단일 프레임 테스트
├── start_backend.py                # 백엔드 서버 실행
├── IMG_8344.MOV                    # 1시간 주차장 영상
├── roi_full_rect_coords.json       # ROI 좌표 데이터
├── best_macos.pt                   # YOLO 차량 인식 모델
├── DanParking_BACKEND/             # Spring Boot 백엔드
└── analysis_results/               # 분석 결과 저장 폴더
```

## 🚀 사용법

### 1. 환경 설정
```bash
# 가상환경 활성화
source yolo_env/bin/activate

# 필요한 패키지 확인
pip list | grep -E "(torch|opencv|requests|numpy)"
```

### 2. 단일 프레임 테스트 (권장)
```bash
# 먼저 시스템이 제대로 작동하는지 테스트
python3 test_single_frame.py
```

### 3. 전체 시스템 실행
```bash
# 백엔드 서버 + 영상 분석 + 데이터 전송
python3 run_parking_system.py
```

### 4. 백엔드 서버만 실행
```bash
# 백엔드 서버만 별도로 실행
python3 start_backend.py
```

## 📊 분석 프로세스

### 🔄 처리 단계
1. **영상 정보 분석**: FPS, 총 프레임 수, 길이 확인
2. **프레임 추출**: 3분 간격으로 특정 시간의 프레임 추출
3. **차량 탐지**: YOLO 모델로 차량 위치 및 신뢰도 계산
4. **ROI 비교**: 차량 중심점이 주차 슬롯 영역 내부에 있는지 확인
5. **상태 결정**: 각 슬롯의 사용 가능/불가능 상태 판단
6. **데이터 전송**: 백엔드 API로 실시간 상태 업데이트
7. **결과 저장**: 분석 이미지와 JSON 데이터 로컬 저장

### 📈 출력 데이터
```json
{
  "timestamp": "2024-08-06T10:30:00",
  "slot_status": [
    {
      "slot_id": "slot_2",
      "is_available": true,
      "vehicle_count": 0,
      "roi_coords": [[491, 818], [521, 840], ...]
    }
  ]
}
```

## 🔧 설정 옵션

### ⚙️ 시스템 파라미터
```python
# parking_analysis_system.py에서 수정 가능
video_path = "IMG_8344.MOV"           # 영상 파일 경로
roi_path = "roi_full_rect_coords.json" # ROI 좌표 파일
model_path = "best_macos.pt"          # YOLO 모델 파일
backend_url = "http://localhost:8080" # 백엔드 서버 URL
interval_minutes = 3                  # 프레임 추출 간격 (분)
```

### 🎯 YOLO 설정
```python
conf_thres = 0.3    # 신뢰도 임계값 (30% 이상)
iou_thres = 0.45    # IoU 임계값
device = 'mps'      # Apple Silicon GPU 사용
```

## 📁 결과 파일

### 🖼️ 이미지 결과
- `analysis_results/frame_YYYYMMDD_HHMMSS.jpg`: ROI와 차량 탐지 결과가 시각화된 이미지
- `test_results/test_frame_Xs.jpg`: 테스트용 결과 이미지

### 📄 JSON 결과
- `analysis_results/result_YYYYMMDD_HHMMSS.json`: 상세 분석 데이터
- `test_results/test_result_Xs.json`: 테스트 결과 데이터

### 📝 로그 파일
- `parking_analysis.log`: 시스템 실행 로그

## 🔍 API 엔드포인트

### 📡 백엔드 전송 API
```
PUT /parking-slots
Content-Type: application/json

{
  "parkingLotId": 1,
  "slotNumber": 2,
  "isAvailable": true
}
```

### 🔐 인증
- Spring Security + JWT 토큰 인증
- `YOLO` 역할 권한 필요

## 🛠️ 문제 해결

### ❌ 일반적인 오류들

**1. 영상 파일을 찾을 수 없음**
```bash
# 파일 경로 확인
ls -la IMG_8344.MOV
```

**2. YOLO 모델 로드 실패**
```bash
# 모델 파일 확인
ls -la best_macos.pt
# 가상환경 활성화 확인
source yolo_env/bin/activate
```

**3. 백엔드 서버 연결 실패**
```bash
# 서버 상태 확인
curl http://localhost:8080/actuator/health
# 포트 사용 확인
lsof -i :8080
```

**4. ROI 좌표 파일 오류**
```bash
# JSON 파일 형식 확인
python3 -c "import json; print(json.load(open('roi_full_rect_coords.json')))"
```

### 🔧 성능 최적화

**1. 처리 속도 향상**
```python
# 배치 크기 조정
batch_size = 1  # 메모리 제한 시
device = 'cpu'  # GPU 없을 때
```

**2. 메모리 사용량 최적화**
```python
# 이미지 크기 조정
img_size = 416  # 기본 640에서 축소
```

## 📞 지원

### 🐛 버그 리포트
- 로그 파일 확인: `parking_analysis.log`
- 테스트 실행: `python3 test_single_frame.py`

### 🔄 업데이트
- YOLO 모델 업데이트: `best_macos.pt` 교체
- ROI 좌표 업데이트: `roi_full_rect_coords.json` 수정

---

**🚗 Happy Parking Analysis! 🎯** 