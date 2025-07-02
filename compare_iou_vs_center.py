import os
import json
import cv2
import csv
import numpy as np
from shapely.geometry import box, Polygon

# ✅ 경로 설정
IMAGE_PATH = r"C:\Users\wecha\project\yolov5\custom_dataset\images\train\Sanggyeonggwan_c3_1.JPG"
YOLO_LABEL_PATH = r"C:\Users\wecha\project\yolov5\runs\detect\exp33\labels\sw_center.txt"
ROI_JSON_PATH = r"C:\Users\wecha\project\yolov5\roi_full_rect_coords.json"
ROI_KEY = "sw_center.JPG"


# ✅ 출력 파일
OUTPUT_CSV = r"C:\Users\wecha\project\yolov5\compare_iou_vs_center.csv"
OUTPUT_IMG = r"C:\Users\wecha\project\yolov5\compare_iou_vs_center.jpg"

# ✅ 이미지 로드
image = cv2.imread(IMAGE_PATH)
if image is None:
    raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {IMAGE_PATH}")
img_h, img_w = image.shape[:2]

# ✅ ROI 로드
with open(ROI_JSON_PATH, "r", encoding="utf-8") as f:
    roi_data = json.load(f)
roi_list = roi_data[ROI_KEY]

# ✅ YOLO 결과 로드
bboxes = []
centers = []
with open(YOLO_LABEL_PATH, "r") as f:
    for line in f:
        parts = list(map(float, line.strip().split()))
        _, xc, yc, w, h = parts[:5]
        xc *= img_w
        yc *= img_h
        w *= img_w
        h *= img_h
        x1 = xc - w / 2
        y1 = yc - h / 2
        x2 = xc + w / 2
        y2 = yc + h / 2
        bboxes.append((x1, y1, x2, y2))
        centers.append((xc, yc))

# ✅ IoU 계산 함수
def calculate_iou(bbox, roi_coords):
    bbox_poly = box(*bbox)
    roi_poly = Polygon(roi_coords)
    if not bbox_poly.intersects(roi_poly):
        return 0.0
    return bbox_poly.intersection(roi_poly).area / bbox_poly.union(roi_poly).area

# ✅ 중심점 판단 함수
def is_center_inside(cx, cy, roi_coords):
    xs = [p[0] for p in roi_coords]
    ys = [p[1] for p in roi_coords]
    return min(xs) <= cx <= max(xs) and min(ys) <= cy <= max(ys)

# ✅ 판단 및 시각화
results = []
for roi in roi_list:
    slot_id = roi["slot_id"]
    coords = roi["coords"]

    # IoU 판단
    max_iou = max([calculate_iou(bbox, coords) for bbox in bboxes], default=0.0)
    iou_status = "occupied" if max_iou >= 0.1 else "free"

    # 중심점 판단
    center_status = "free"
    for cx, cy in centers:
        if is_center_inside(cx, cy, coords):
            center_status = "occupied"
            break

    # 판단 비교
    match = "일치" if iou_status == center_status else "불일치"

    # 시각화 색상 지정
    if iou_status == "occupied" and center_status == "occupied":
        color = (0, 0, 255)      # 빨강
    elif iou_status == "free" and center_status == "free":
        color = (0, 255, 0)      # 초록
    elif iou_status == "occupied" and center_status == "free":
        color = (255, 0, 0)      # 파랑
    else:
        color = (0, 165, 255)    # 주황

    # 사각형 그리기
    pts = [tuple(map(int, pt)) for pt in coords]
    cv2.polylines(image, [np.array(pts)], isClosed=True, color=color, thickness=2)
    cv2.putText(image, slot_id, pts[0], cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

    results.append((slot_id, iou_status, center_status, match))

# ✅ 결과 CSV 저장
with open(OUTPUT_CSV, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['slot_id', 'iou_status', 'center_status', 'match'])
    for row in results:
        writer.writerow(row)

# ✅ 시각화 이미지 저장
cv2.imwrite(OUTPUT_IMG, image)
print(f"✅ 완료: {OUTPUT_CSV}")
print(f"🖼️ 저장됨: {OUTPUT_IMG}")
