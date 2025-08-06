#!/usr/bin/env python3
"""
30분 지점 영상 프레임 추출
"""

import cv2
import os

def extract_frame_at_30min():
    """30분 지점의 프레임 추출"""
    
    video_path = "IMG_8344.MOV"
    
    if not os.path.exists(video_path):
        print(f"❌ 영상 파일을 찾을 수 없습니다: {video_path}")
        return False
    
    # 영상 열기
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"❌ 영상을 열 수 없습니다: {video_path}")
        return False
    
    # 영상 정보 가져오기
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps
    
    print(f"📹 영상 정보:")
    print(f"  • FPS: {fps:.2f}")
    print(f"  • 총 프레임: {total_frames}")
    print(f"  • 총 길이: {duration/60:.1f}분")
    
    # 30분 지점 계산 (초 단위)
    target_time = 30 * 60  # 30분 = 1800초
    target_frame = int(target_time * fps)
    
    print(f"🎯 추출할 프레임:")
    print(f"  • 시간: {target_time/60:.1f}분 ({target_time}초)")
    print(f"  • 프레임 번호: {target_frame}")
    
    # 해당 프레임으로 이동
    cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
    
    # 프레임 읽기
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("❌ 프레임을 읽을 수 없습니다.")
        return False
    
    # 프레임 저장
    output_path = "frame_30min.jpg"
    cv2.imwrite(output_path, frame)
    
    print(f"✅ 프레임 추출 완료:")
    print(f"  • 파일: {output_path}")
    print(f"  • 크기: {frame.shape[1]}×{frame.shape[0]}")
    
    return True

if __name__ == "__main__":
    print("📸 30분 지점 프레임 추출")
    print("=" * 40)
    
    success = extract_frame_at_30min()
    
    if success:
        print("\n🎯 다음 단계:")
        print("1. frame_30min.jpg 파일을 확인")
        print("2. roi_coordinate_tool.py로 ROI 좌표 찍기")
    else:
        print("\n❌ 프레임 추출 실패") 