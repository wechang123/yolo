# VM 배포 가이드 (Linux 환경)

## 🚀 **VM에서 주차장 점유 현황 시스템 배포**

### 📋 **사전 요구사항**

1. **Python 3.8+ 설치**
2. **Git 설치**
3. **Docker (선택사항 - 백엔드용)**

### 🔧 **1단계: 코드 다운로드**

```bash
# Git 저장소 클론
git clone https://github.com/wechang123/yolo.git
cd yolo

# 또는 기존 저장소 업데이트
git pull origin main
```

### 🐍 **2단계: Python 환경 설정**

```bash
# Python 가상환경 생성
python3 -m venv yolo_env
source yolo_env/bin/activate

# 필요한 패키지 설치
pip install -r requirements.txt

# 추가 패키지 (Linux 환경)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### 📁 **3단계: 필요한 파일 확인**

다음 파일들이 있는지 확인:
- `parking_occupancy_analyzer.py` - 메인 분석 스크립트
- `parking_scheduler.py` - 스케줄러
- `roi_manual_coords.json` - ROI 좌표
- `best_macos.pt` - YOLO 모델 (Linux용으로 변환 필요)
- `frame_30min.jpg` - 분석할 이미지

### 🔄 **4단계: YOLO 모델 변환 (필요시)**

macOS에서 훈련된 모델을 Linux에서 사용하려면:

```bash
# 모델 변환 (선택사항)
python3 -c "
import torch
model = torch.load('best_macos.pt', map_location='cpu')
torch.save(model, 'best_linux.pt')
"
```

### 🏃‍♂️ **5단계: 백엔드 서버 설정**

#### 옵션 A: Docker 사용 (권장)

```bash
# Docker 설치 확인
docker --version

# 백엔드 빌드 및 실행
cd DanParking_BACKEND
docker build -t danparking-backend .
docker run -d -p 8080:8080 --name danparking-backend danparking-backend
```

#### 옵션 B: 직접 실행

```bash
# Java 11+ 설치 확인
java -version

# 백엔드 실행
cd DanParking_BACKEND
./gradlew bootRun
```

### 🧪 **6단계: 테스트 실행**

```bash
# 가상환경 활성화
source yolo_env/bin/activate

# 단일 분석 테스트
python3 parking_occupancy_analyzer.py

# 시각화 테스트
python3 visualize_occupancy.py --iou 0.17 --output test_visualization.jpg

# 디버그 분석
python3 debug_occupancy_analysis.py
```

### ⏰ **7단계: 스케줄러 실행**

```bash
# 백그라운드에서 스케줄러 실행
nohup python3 parking_scheduler.py > scheduler.log 2>&1 &

# 로그 확인
tail -f scheduler.log
```

### 📊 **8단계: 모니터링**

```bash
# 프로세스 확인
ps aux | grep python

# 로그 확인
tail -f parking_occupancy.log

# 백엔드 상태 확인
curl http://localhost:8080/parking-lots/occupancy/sanggyeonggwan
```

### 🔧 **9단계: 시스템 서비스 등록 (선택사항)**

```bash
# systemd 서비스 파일 생성
sudo nano /etc/systemd/system/parking-occupancy.service
```

서비스 파일 내용:
```ini
[Unit]
Description=Parking Occupancy Analysis System
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/yolo
Environment=PATH=/path/to/yolo/yolo_env/bin
ExecStart=/path/to/yolo/yolo_env/bin/python parking_scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

서비스 등록:
```bash
sudo systemctl daemon-reload
sudo systemctl enable parking-occupancy
sudo systemctl start parking-occupancy
```

### 🐛 **문제 해결**

#### 1. **CUDA 오류**
```bash
# CPU 전용으로 실행
export CUDA_VISIBLE_DEVICES=""
python3 parking_occupancy_analyzer.py
```

#### 2. **메모리 부족**
```bash
# 메모리 사용량 확인
free -h
# 필요시 swap 추가
```

#### 3. **포트 충돌**
```bash
# 포트 사용 확인
netstat -tulpn | grep 8080
# 다른 포트 사용
```

### 📈 **성능 최적화**

1. **GPU 사용** (가능한 경우):
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

2. **메모리 최적화**:
   ```bash
   # 배치 크기 조정
   export BATCH_SIZE=1
   ```

3. **로깅 최적화**:
   ```bash
   # 로그 레벨 조정
   export LOG_LEVEL=INFO
   ```

### 🔒 **보안 고려사항**

1. **방화벽 설정**:
   ```bash
   sudo ufw allow 8080
   ```

2. **SSL 인증서 설정** (프로덕션용):
   ```bash
   # Let's Encrypt 사용
   sudo certbot --nginx
   ```

### 📞 **지원**

문제가 발생하면 다음을 확인:
1. 로그 파일: `parking_occupancy.log`, `scheduler.log`
2. 시스템 리소스: `htop`, `df -h`
3. 네트워크 연결: `ping`, `curl`

---

## 🎯 **최종 확인 사항**

- [ ] Git 저장소 클론 완료
- [ ] Python 환경 설정 완료
- [ ] YOLO 모델 파일 존재
- [ ] ROI 좌표 파일 존재
- [ ] 백엔드 서버 실행 중
- [ ] 단일 분석 테스트 성공
- [ ] 스케줄러 실행 중
- [ ] 로그 모니터링 중

**모든 단계가 완료되면 시스템이 정상적으로 작동합니다!** 🚀
