import cv2
import json
import os

# === 경로 설정 ===
image_path = r"C:\Users\wecha\project\yolov5\custom_dataset\images\train\Sanggyeonggwan_c1_1.jpeg"
output_json = r"C:\Users\wecha\project\yolov5\roi_slots.json"
image_name = os.path.basename(image_path)

scale_ratio = 0.3  # 원본이 크니까 30% 크기로 축소해서 띄움

roi_data = {}
clicked_points = []

def click_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        orig_x = int(x / scale_ratio)
        orig_y = int(y / scale_ratio)
        clicked_points.append([orig_x, orig_y])
        print(f"📌 클릭: ({orig_x}, {orig_y})")
        cv2.circle(param, (x, y), 4, (0, 255, 0), -1)
        cv2.imshow("ROI Annotator", param)

        if len(clicked_points) % 2 == 0:
            x1, y1 = clicked_points[-2]
            x2, y2 = clicked_points[-1]
            if image_name not in roi_data:
                roi_data[image_name] = []
            roi_data[image_name].append([x1, y1, x2, y2])
            print(f"✅ ROI #{len(roi_data[image_name])} 저장됨")
            cv2.rectangle(param, (int(x1 * scale_ratio), int(y1 * scale_ratio)),
                          (int(x2 * scale_ratio), int(y2 * scale_ratio)), (255, 0, 0), 2)
            cv2.imshow("ROI Annotator", param)

# === 이미지 로딩 ===
img = cv2.imread(image_path)
if img is None:
    print("❌ 이미지 로드 실패:", image_path)
    exit()

display_img = cv2.resize(img, (0, 0), fx=scale_ratio, fy=scale_ratio)

cv2.imshow("ROI Annotator", display_img)
cv2.setMouseCallback("ROI Annotator", click_callback, display_img.copy())

print(f"\n▶ 이미지: {image_name}")
print("   슬롯 하나당 클릭 2번 (좌상단 → 우하단)")
print("   ESC 키 누르면 저장 종료")

while True:
    key = cv2.waitKey(0) & 0xFF
    if key == 27:  # ESC
        break

cv2.destroyAllWindows()

with open(output_json, 'w') as f:
    json.dump(roi_data, f, indent=2)

print(f"\n✅ ROI 좌표가 저장되었습니다 → {output_json}")
