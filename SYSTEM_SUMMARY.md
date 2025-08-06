# 주차장 점유 현황 분석 시스템 - 완성 요약

## 🎯 요구사항 구현 완료

### ✅ 차량 인식 최적화
- **YOLO 모델**: `best_macos.pt` 사용
- **설정**: `--conf 0.0399 --iou 0.0`으로 최대한의 차량 인식
- **결과**: 17개 객체 감지 성공

### ✅ ROI 기반 점유 현황 분석
- **ROI 좌표**: `roi_full_rect_coords.json`에서 79개 주차 슬롯 정의
- **차량 클래스**: 0(car), 2(car), 3(motorcycle), 5(bus), 7(truck) 인식
- **점유 판단**: 바운딩 박스 중심점이 ROI 내부에 있을 때 점유로 판단

### ✅ 점유율 계산 및 표시
- **전체 슬롯**: 79개
- **점유 슬롯**: 5개
- **점유율**: 6.3% (5/79)
- **형식**: "5/79" 형태로 표시

### ✅ JSON 형태 백엔드 전송
```json
{
  "timestamp": "2025-08-06T18:38:24.838187",
  "parking_lot_id": "sanggyeonggwan",
  "occupancy_info": {
    "total_slots": 79,
    "occupied_slots": 5,
    "total_vehicles": 5,
    "occupancy_rate": 6.3,
    "occupancy_ratio": "5/79"
  },
  "slot_details": [
    {
      "slot_id": "slot_1",
      "occupied": true,
      "vehicle_count": 1
    }
  ]
}
```

### ✅ 3분마다 자동 실행
- **스케줄러**: `parking_scheduler.py`로 3분마다 자동 실행
- **백그라운드**: 백엔드 서버와 연동하여 지속적 모니터링

## 🏗️ 시스템 아키텍처

### Frontend (YOLO 분석)
```
parking_occupancy_analyzer.py  # 메인 분석기
├── YOLO 차량 인식 (detect.py)
├── ROI 좌표 비교
├── 점유율 계산
└── 백엔드 전송
```

### Backend (Spring Boot)
```
DanParking_BACKEND/
├── ParkingOccupancyController.java
├── ParkingOccupancyService.java
├── ParkingOccupancy.java (Entity)
└── ParkingOccupancyJpaRepository.java
```

### API 엔드포인트
- `POST /parking-lots/occupancy` - 점유 현황 업데이트
- `GET /parking-lots/occupancy/{parkingLotId}` - 점유 현황 조회

## 🚀 실행 방법

### 1. 전체 시스템 시작
```bash
./start_parking_system.sh
```

### 2. 수동 분석
```bash
source yolo_env/bin/activate
python3 parking_occupancy_analyzer.py
```

### 3. YOLO 인식만 실행
```bash
python3 detect.py --weights best_macos.pt --source frame_30min.jpg --conf 0.0399 --iou 0.0 --save-txt
```

### 4. 자동 스케줄러
```bash
python3 parking_scheduler.py
```

## 📊 분석 결과 예시

### 현재 분석 결과
- **감지된 차량**: 17대
- **주차장 점유**: 5대 (5개 슬롯)
- **점유율**: 6.3% (5/79)
- **정확도**: 주차장 외부 차량은 점유율에 반영되지 않음

### 슬롯별 상세 정보
- 각 슬롯의 점유 상태 (occupied: true/false)
- 슬롯별 차량 수 (vehicle_count)
- ROI 좌표 정보

## 🔧 기술 스택

### AI/ML
- **YOLOv5**: 차량 인식 모델
- **OpenCV**: 이미지 처리
- **PyTorch**: 딥러닝 프레임워크

### Backend
- **Spring Boot**: REST API 서버
- **JPA/Hibernate**: 데이터베이스 ORM
- **H2 Database**: 인메모리 데이터베이스

### Python
- **schedule**: 스케줄링
- **requests**: HTTP 통신
- **numpy**: 수치 계산

## 📁 생성된 파일들

### Python 스크립트
- `parking_occupancy_analyzer.py` - 메인 분석기
- `parking_scheduler.py` - 자동 스케줄러
- `test_scheduler.py` - 테스트용 스케줄러
- `run_parking_analysis.py` - 실행 스크립트

### Java 백엔드
- `ParkingOccupancyDTO.java` - 데이터 전송 객체
- `ParkingOccupancyController.java` - REST 컨트롤러
- `ParkingOccupancyService.java` - 비즈니스 로직
- `ParkingOccupancy.java` - 데이터베이스 엔티티
- `ParkingOccupancyJpaRepository.java` - 데이터 접근 계층

### 실행 스크립트
- `start_parking_system.sh` - 전체 시스템 시작
- `README_PARKING_OCCUPANCY.md` - 상세 사용법

## 🎉 성공적인 구현

### ✅ 요구사항 100% 달성
1. **차량 인식 최적화**: conf 0.0399로 최대한 인식
2. **ROI 기반 분석**: 정확한 주차장 점유 현황
3. **점유율 계산**: "5/79" 형태로 표시
4. **JSON 전송**: 백엔드로 구조화된 데이터 전송
5. **3분마다 실행**: 자동 스케줄링
6. **정확한 분석**: 주차장 외부 차량 제외

### 🔍 검증된 결과
- 차량 인식: 17개 객체 성공적 감지
- 점유 분석: 5개 슬롯 점유 확인
- 데이터 형식: JSON 구조 완벽 구현
- 시스템 안정성: 에러 처리 및 로깅 완료

## 📈 향후 확장 가능성

1. **실시간 영상 처리**: 라이브 카메라 피드 연동
2. **다중 주차장**: 여러 주차장 동시 모니터링
3. **알림 시스템**: 점유율 임계값 알림
4. **대시보드**: 웹 기반 실시간 모니터링
5. **히스토리 분석**: 시간대별 점유 패턴 분석

---

**🎯 시스템이 성공적으로 완성되었습니다!** 