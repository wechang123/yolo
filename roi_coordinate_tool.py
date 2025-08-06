#!/usr/bin/env python3
"""
ROI 좌표 찍기 도구
마우스로 4개 점을 찍어서 사각형을 만들고, 확대/축소 및 미세 조정 가능
"""

import cv2
import numpy as np
import json
import os

class ROICoordinateTool:
    def __init__(self, image_path="frame_30min.jpg"):
        self.image_path = image_path
        self.original_image = None
        self.display_image = None
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.points = []
        self.current_rectangles = []
        self.selected_point = None
        self.dragging = False
        self.window_name = "ROI 좌표 찍기 도구"
        
        # 마우스 콜백 설정
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        
        # 키보드 안내
        self.print_instructions()
    
    def print_instructions(self):
        """사용법 안내"""
        print("\n🎯 ROI 좌표 찍기 도구 사용법")
        print("=" * 50)
        print("마우스:")
        print("  • 좌클릭: 점 추가 (4개까지)")
        print("  • 우클릭: 점 삭제")
        print("  • 드래그: 점 이동")
        print("")
        print("키보드:")
        print("  • + / -: 확대/축소")
        print("  • 방향키: 이미지 이동")
        print("  • R: 모든 점 삭제")
        print("  • S: 현재 사각형 저장")
        print("  • L: 저장된 사각형 불러오기")
        print("  • Q: 종료")
        print("")
        print("팁:")
        print("  • 확대해서 정확한 위치에 점을 찍으세요")
        print("  • 4개 점이 찍히면 자동으로 사각형이 그려집니다")
        print("  • 점을 드래그해서 미세 조정이 가능합니다")
    
    def load_image(self):
        """이미지 로드"""
        if not os.path.exists(self.image_path):
            print(f"❌ 이미지 파일을 찾을 수 없습니다: {self.image_path}")
            return False
        
        self.original_image = cv2.imread(self.image_path)
        if self.original_image is None:
            print(f"❌ 이미지를 읽을 수 없습니다: {self.image_path}")
            return False
        
        self.display_image = self.original_image.copy()
        print(f"✅ 이미지 로드 완료: {self.image_path}")
        print(f"   크기: {self.original_image.shape[1]}×{self.original_image.shape[0]}")
        return True
    
    def mouse_callback(self, event, x, y, flags, param):
        """마우스 콜백 함수"""
        # 좌표 변환 (확대/축소 및 오프셋 적용)
        real_x = int((x - self.offset_x) / self.scale)
        real_y = int((y - self.offset_y) / self.scale)
        
        if event == cv2.EVENT_LBUTTONDOWN:
            # 좌클릭: 점 추가
            if len(self.points) < 4:
                self.points.append([real_x, real_y])
                print(f"✅ 점 {len(self.points)} 추가: ({real_x}, {real_y})")
                
                # 4개 점이 찍히면 사각형 생성
                if len(self.points) == 4:
                    self.create_rectangle()
            else:
                # 점 선택 (드래그용)
                self.selected_point = self.find_nearest_point(real_x, real_y)
                if self.selected_point is not None:
                    self.dragging = True
        
        elif event == cv2.EVENT_MOUSEMOVE and self.dragging:
            # 드래그 중: 점 이동
            if self.selected_point is not None:
                self.points[self.selected_point] = [real_x, real_y]
                print(f"🔄 점 {self.selected_point + 1} 이동: ({real_x}, {real_y})")
                self.update_rectangle()
        
        elif event == cv2.EVENT_LBUTTONUP:
            # 드래그 종료
            self.dragging = False
            self.selected_point = None
        
        elif event == cv2.EVENT_RBUTTONDOWN:
            # 우클릭: 점 삭제
            point_idx = self.find_nearest_point(real_x, real_y)
            if point_idx is not None:
                removed_point = self.points.pop(point_idx)
                print(f"❌ 점 {point_idx + 1} 삭제: ({removed_point[0]}, {removed_point[1]})")
                self.update_rectangle()
    
    def find_nearest_point(self, x, y, threshold=20):
        """가장 가까운 점 찾기"""
        for i, point in enumerate(self.points):
            distance = np.sqrt((point[0] - x)**2 + (point[1] - y)**2)
            if distance < threshold:
                return i
        return None
    
    def create_rectangle(self):
        """사각형 생성"""
        if len(self.points) == 4:
            # 점들을 시계방향으로 정렬
            center_x = sum(p[0] for p in self.points) / 4
            center_y = sum(p[1] for p in self.points) / 4
            
            # 각도로 정렬
            angles = []
            for point in self.points:
                angle = np.arctan2(point[1] - center_y, point[0] - center_x)
                angles.append(angle)
            
            sorted_points = [p for _, p in sorted(zip(angles, self.points))]
            self.points = sorted_points
            
            self.current_rectangles.append({
                'points': self.points.copy(),
                'slot_id': f'slot_{len(self.current_rectangles) + 1}'
            })
            
            print(f"✅ 사각형 {len(self.current_rectangles)} 생성 완료")
            print(f"   슬롯 ID: {self.current_rectangles[-1]['slot_id']}")
            
            # 새로운 점들을 위해 초기화
            self.points = []
    
    def update_rectangle(self):
        """사각형 업데이트"""
        if self.current_rectangles:
            # 마지막 사각형 업데이트
            if len(self.points) == 4:
                center_x = sum(p[0] for p in self.points) / 4
                center_y = sum(p[1] for p in self.points) / 4
                angles = []
                for point in self.points:
                    angle = np.arctan2(point[1] - center_y, point[0] - center_x)
                    angles.append(angle)
                sorted_points = [p for _, p in sorted(zip(angles, self.points))]
                self.current_rectangles[-1]['points'] = sorted_points
    
    def draw_image(self):
        """이미지 그리기 (개선된 버전)"""
        # 원본 이미지 복사
        self.display_image = self.original_image.copy()
        
        # 확대/축소 적용
        height, width = self.original_image.shape[:2]
        new_width = int(width * self.scale)
        new_height = int(height * self.scale)
        
        # 이미지 리사이즈
        resized_image = cv2.resize(self.original_image, (new_width, new_height))
        
        # 캔버스 크기 계산 (오프셋 포함)
        canvas_width = new_width + abs(self.offset_x)
        canvas_height = new_height + abs(self.offset_y)
        
        # 캔버스 생성
        canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)
        
        # 이미지 배치
        y_offset = max(0, self.offset_y)
        x_offset = max(0, self.offset_x)
        
        # 이미지가 캔버스 범위 내에 있는지 확인
        if (x_offset < canvas_width and y_offset < canvas_height and 
            x_offset + new_width > 0 and y_offset + new_height > 0):
            
            # 이미지 영역 계산
            img_start_x = max(0, -x_offset)
            img_start_y = max(0, -y_offset)
            img_end_x = min(new_width, canvas_width - x_offset)
            img_end_y = min(new_height, canvas_height - y_offset)
            
            canvas_start_x = max(0, x_offset)
            canvas_start_y = max(0, y_offset)
            canvas_end_x = min(canvas_width, x_offset + new_width)
            canvas_end_y = min(canvas_height, y_offset + new_height)
            
            # 이미지 복사
            canvas[canvas_start_y:canvas_end_y, canvas_start_x:canvas_end_x] = \
                resized_image[img_start_y:img_end_y, img_start_x:img_end_x]
        
        self.display_image = canvas
        
        # 점 그리기
        for i, point in enumerate(self.points):
            x, y = point
            display_x = int(x * self.scale + self.offset_x)
            display_y = int(y * self.scale + self.offset_y)
            
            # 점이 캔버스 범위 내에 있는지 확인
            if (0 <= display_x < canvas_width and 0 <= display_y < canvas_height):
                # 점 그리기
                cv2.circle(self.display_image, (display_x, display_y), 5, (0, 255, 0), -1)
                cv2.circle(self.display_image, (display_x, display_y), 7, (255, 255, 255), 2)
                
                # 번호 표시
                cv2.putText(self.display_image, str(i+1), (display_x+10, display_y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 사각형 그리기
        for rect in self.current_rectangles:
            points = rect['points']
            slot_id = rect['slot_id']
            
            # 변환된 좌표
            display_points = []
            for point in points:
                x, y = point
                display_x = int(x * self.scale + self.offset_x)
                display_y = int(y * self.scale + self.offset_y)
                display_points.append([display_x, display_y])
            
            # 사각형 그리기
            pts = np.array(display_points, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(self.display_image, [pts], True, (0, 255, 0), 2)
            
            # 슬롯 ID 표시
            center_x = sum(p[0] for p in display_points) // 4
            center_y = sum(p[1] for p in display_points) // 4
            cv2.putText(self.display_image, slot_id, (center_x-20, center_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # 정보 표시
        info_text = f"점: {len(self.points)}/4 | 사각형: {len(self.current_rectangles)} | 확대: {self.scale:.1f}x"
        cv2.putText(self.display_image, info_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    def save_rectangles(self):
        """사각형 저장"""
        if not self.current_rectangles:
            print("❌ 저장할 사각형이 없습니다.")
            return
        
        # JSON 형식으로 저장
        roi_data = {
            "frame_30min.jpg": []
        }
        
        for rect in self.current_rectangles:
            roi_data["frame_30min.jpg"].append({
                "slot_id": rect['slot_id'],
                "coords": rect['points']
            })
        
        output_path = "roi_manual_coords.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(roi_data, f, ensure_ascii=False, indent=4)
        
        print(f"✅ ROI 좌표 저장 완료: {output_path}")
        print(f"   총 {len(self.current_rectangles)}개 사각형")
        
        # 미리보기 이미지 생성
        preview_image = self.original_image.copy()
        for rect in self.current_rectangles:
            points = rect['points']
            slot_id = rect['slot_id']
            
            pts = np.array(points, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(preview_image, [pts], True, (0, 255, 0), 2)
            
            center_x = sum(p[0] for p in points) // 4
            center_y = sum(p[1] for p in points) // 4
            cv2.putText(preview_image, slot_id, (center_x-20, center_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        cv2.imwrite("roi_manual_preview.jpg", preview_image)
        print(f"✅ 미리보기 저장: roi_manual_preview.jpg")
    
    def load_rectangles(self):
        """저장된 사각형 불러오기"""
        if os.path.exists("roi_manual_coords.json"):
            with open("roi_manual_coords.json", 'r', encoding='utf-8') as f:
                roi_data = json.load(f)
            
            if "frame_30min.jpg" in roi_data:
                self.current_rectangles = []
                for slot_data in roi_data["frame_30min.jpg"]:
                    self.current_rectangles.append({
                        'slot_id': slot_data['slot_id'],
                        'points': slot_data['coords']
                    })
                print(f"✅ {len(self.current_rectangles)}개 사각형 불러오기 완료")
            else:
                print("❌ 호환되는 데이터가 없습니다.")
        else:
            print("❌ 저장된 파일이 없습니다.")
    
    def run(self):
        """메인 실행 함수"""
        if not self.load_image():
            return
        
        print("\n🎯 ROI 좌표 찍기를 시작합니다...")
        print("이미지 창에서 마우스로 점을 찍으세요!")
        
        while True:
            self.draw_image()
            cv2.imshow(self.window_name, self.display_image)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('+') or key == ord('='):
                self.scale = min(3.0, self.scale + 0.1)
                print(f"🔍 확대: {self.scale:.1f}x")
            elif key == ord('-'):
                self.scale = max(0.1, self.scale - 0.1)
                print(f"🔍 축소: {self.scale:.1f}x")
            elif key == ord('r'):
                self.points = []
                self.current_rectangles = []
                print("🔄 모든 점과 사각형 삭제")
            elif key == ord('s'):
                self.save_rectangles()
            elif key == ord('l'):
                self.load_rectangles()
            elif key == 82:  # 위쪽 화살표
                self.offset_y = max(-1000, self.offset_y - 20)
            elif key == 84:  # 아래쪽 화살표
                self.offset_y = min(1000, self.offset_y + 20)
            elif key == 81:  # 왼쪽 화살표
                self.offset_x = max(-1000, self.offset_x - 20)
            elif key == 83:  # 오른쪽 화살표
                self.offset_x = min(1000, self.offset_x + 20)
        
        cv2.destroyAllWindows()
        print("\n✅ ROI 좌표 찍기 완료!")

if __name__ == "__main__":
    tool = ROICoordinateTool()
    tool.run() 