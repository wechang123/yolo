#!/usr/bin/env python3
"""
Windows에서 저장된 YOLO 모델을 macOS에서 사용할 수 있게 변환하는 스크립트
WindowsPath 객체를 제거하고 호환 가능한 형태로 저장합니다.
"""

import torch
import pickle
import pathlib
from pathlib import PosixPath

def convert_windows_model_to_macos(input_path, output_path):
    """Windows 모델을 macOS 호환 모델로 변환"""
    
    # 원본 pathlib를 백업
    original_windows_path = pathlib.WindowsPath
    
    # WindowsPath를 PosixPath로 대체
    pathlib.WindowsPath = pathlib.PosixPath
    
    try:
        print(f"모델 로딩 중: {input_path}")
        # 모델 로드 (weights_only=False로 안전하게)
        checkpoint = torch.load(input_path, map_location='cpu', weights_only=False)
        
        print("모델 로드 완료!")
        print(f"모델 키: {list(checkpoint.keys())}")
        
        # 경로 관련 정보를 정리
        if 'optimizer' in checkpoint:
            del checkpoint['optimizer']  # 옵티마이저 정보 제거 (경로 문제 방지)
            
        if 'ema' in checkpoint and checkpoint['ema']:
            # EMA 모델에서도 경로 정보 정리
            ema = checkpoint['ema']
            if hasattr(ema, 'updates'):
                ema.updates = torch.tensor(ema.updates) if not isinstance(ema.updates, torch.Tensor) else ema.updates
        
        print(f"정리된 모델 저장 중: {output_path}")
        torch.save(checkpoint, output_path)
        print("모델 변환 완료!")
        
        # 변환된 모델 테스트
        print("변환된 모델 테스트 중...")
        test_checkpoint = torch.load(output_path, map_location='cpu', weights_only=False)
        print("✅ 변환된 모델 로드 성공!")
        
        return True
        
    except Exception as e:
        print(f"❌ 변환 실패: {e}")
        return False
    
    finally:
        # 원본 pathlib 복원
        pathlib.WindowsPath = original_windows_path

if __name__ == "__main__":
    # 두 모델 모두 변환 시도
    models_to_convert = [
        ("best.pt", "best_macos.pt"),
        ("shared_model/best.pt", "shared_model/best_macos.pt")
    ]
    
    for input_model, output_model in models_to_convert:
        print(f"\n{'='*50}")
        print(f"변환 중: {input_model} → {output_model}")
        print(f"{'='*50}")
        
        try:
            success = convert_windows_model_to_macos(input_model, output_model)
            if success:
                print(f"✅ {input_model} 변환 성공!")
            else:
                print(f"❌ {input_model} 변환 실패!")
        except FileNotFoundError:
            print(f"⚠️  파일을 찾을 수 없습니다: {input_model}")
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}")
    
    print(f"\n{'='*50}")
    print("모든 변환 작업 완료!")
    print(f"{'='*50}")