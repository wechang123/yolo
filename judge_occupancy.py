import os
import json
import cv2
import csv
import numpy as np
from shapely.geometry import box, Polygon

# ✅ 경로 설정
IMAGE_PATH = r"C:\Users\wecha\project\yolov5\custom_dataset\images\train\Sanggyeonggwan_c3_1.JPG"
YOLO_LABEL_PATH = r"C:\Users\wecha\project\yolov5\runs\detect\exp55\labels\Sanggyeonggwan_c3_1.txt"
ROI_JSON_PATH = r"C:\Users\wecha\project\yolov5\roi_full_rect_coords.json"
ROI_KEY = "sw_center.JPG"
EXCLUDE_KEY = "Sanggyeonggwan_c1_1.jpeg"  # 제외할 영역

OUTPUT_CSV_PATH = r"C:\Users\wecha\project\yolov5\occupancy_result_iou.csv"
OUTPUT_IMAGE_PATH = r"C:\Users\wecha\project\yolov5\result_with_roi_iou.jpg"

# ✅ 이미지 로드
image = cv2.imread(IMAGE_PATH)
if image is None:
    raise FileNotFoundError(f"이미지를 찾을 수 없습니다: {IMAGE_PATH}")
img_h, img_w = image.shape[:2]

# ✅ ROI JSON 로드
with open(ROI_JSON_PATH, 'r', encoding="utf-8") as f:
    roi_data = json.load(f)

if ROI_KEY not in roi_data:
    raise KeyError(f"ROI JSON에 '{ROI_KEY}' 키가 없습니다.")
roi_list = roi_data[ROI_KEY]

exclude_list = roi_data.get(EXCLUDE_KEY, [])

# ✅ 중복 제거 함수
def calculate_iou_bbox_roi(roi1, roi2):
    poly1 = Polygon(roi1)
    poly2 = Polygon(roi2)
    if not poly1.is_valid or not poly2.is_valid or not poly1.intersects(poly2):
        return 0.0
    return poly1.intersection(poly2).area / poly1.union(poly2).area

filtered_roi_list = []
for roi in roi_list:
    coords = roi["coords"]
    if all(calculate_iou_bbox_roi(coords, ex["coords"]) < 0.5 for ex in exclude_list):
        filtered_roi_list.append(roi)

# ✅ YOLO 결과 로드
bboxes = []
with open(YOLO_LABEL_PATH, 'r') as f:
    for line in f.readlines():
        parts = list(map(float, line.strip().split()))
        cls, xc, yc, w, h = parts[:5]
        x_center = xc * img_w
        y_center = yc * img_h
        width = w * img_w
        height = h * img_h
        x1 = x_center - width / 2
        y1 = y_center - height / 2
        x2 = x_center + width / 2
        y2 = y_center + height / 2
        bboxes.append((x1, y1, x2, y2))

# ✅ IoU 계산 함수
def calculate_iou(bbox, roi_coords):
    bbox_poly = box(*bbox)
    roi_poly = Polygon(roi_coords)
    if not bbox_poly.intersects(roi_poly):
        return 0.0
    return bbox_poly.intersection(roi_poly).area / bbox_poly.union(roi_poly).area

# ✅ Occupied / Free 판단
results = []
for roi in filtered_roi_list:
    slot_id = roi["slot_id"]
    coords = roi["coords"]
    max_iou = max([calculate_iou(bbox, coords) for bbox in bboxes], default=0.0)
    status = 'occupied' if max_iou >= 0.1 else 'free'
    results.append((slot_id, status, coords))

# ✅ CSV 저장
with open(OUTPUT_CSV_PATH, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['slot_id', 'status'])
    for slot_id, status, _ in results:
        writer.writerow([slot_id, status])

# ✅ 이미지 시각화
for slot_id, status, coords in results:
    pts = [tuple(map(int, pt)) for pt in coords]
    color = (0, 255, 0) if status == 'free' else (0, 0, 255)
    cv2.polylines(image, [np.array(pts)], isClosed=True, color=color, thickness=2)
    cv2.putText(image, slot_id, pts[0], cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

cv2.imwrite(OUTPUT_IMAGE_PATH, image)
print(f"✅ 완료: {OUTPUT_CSV_PATH}, {OUTPUT_IMAGE_PATH}")
