#!/usr/bin/env python3
"""
macOS에서 훈련된 YOLO 모델을 Linux용으로 변환
"""

import torch
import os
import sys

def convert_model():
    """모델 변환 함수"""
    try:
        # 입력 모델 경로
        input_model = "best_macos.pt"
        output_model = "best_linux.pt"
        
        if not os.path.exists(input_model):
            print(f"오류: {input_model} 파일이 없습니다.")
            return False
        
        print(f"모델 변환 시작: {input_model} → {output_model}")
        
        # 모델 로드 (CPU로 강제)
        model = torch.load(input_model, map_location='cpu')
        
        # 모델 저장 (Linux 호환)
        torch.save(model, output_model, _use_new_zipfile_serialization=False)
        
        print(f"모델 변환 완료: {output_model}")
        
        # 파일 크기 확인
        if os.path.exists(output_model):
            size = os.path.getsize(output_model) / (1024 * 1024)  # MB
            print(f"변환된 모델 크기: {size:.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"모델 변환 실패: {e}")
        return False

if __name__ == "__main__":
    success = convert_model()
    if success:
        print("✅ 모델 변환 성공!")
    else:
        print("❌ 모델 변환 실패!")
        sys.exit(1)
