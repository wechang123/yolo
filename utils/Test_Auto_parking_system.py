import os
import time
import json
import requests
import subprocess
from datetime import datetime
from shapely.geometry import box, Polygon
import cv2
import numpy as np

# ✅ 설정값
YOLO_WEIGHTS = "best.pt"
YOLO_IMG_SIZE = 640
CAMERA_CONFIG = {
    "cam1": {
        "image_path": "input/cam1.jpg",
        "roi_key": "sw_center.JPG"
    },
    "cam2": {
        "image_path": "input/cam2.jpg",
        "roi_key": "Sanggyeonggwan_c1_1.jpeg"
    }
}
ROI_JSON_PATH = "roi_full_rect_coords.json"
YOLO_LABEL_DIR = "runs/detect/exp/labels"
API_ENDPOINT = "https://your.backend/api/parking/update"
AUTH_HEADER = {"Authorization": "Bearer YOUR_TOKEN_HERE"}

# ✅ ROI 로드
with open(ROI_JSON_PATH, "r", encoding="utf-8") as f:
    ROI_DATA = json.load(f)

def run_yolo(image_path):
    subprocess.run([
        "python", "detect.py",
        "--weights", YOLO_WEIGHTS,
        "--source", image_path,
        "--save-txt", "--save-conf",
        "--img", str(YOLO_IMG_SIZE)
    ], check=True)

def parse_yolo_result(label_path, img_w, img_h):
    bboxes = []
    if not os.path.exists(label_path):
        return bboxes
    with open(label_path, 'r') as f:
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
    return bboxes

def calculate_iou(bbox, roi_coords):
    bbox_poly = box(*bbox)
    roi_poly = Polygon(roi_coords)
    if not bbox_poly.intersects(roi_poly):
        return 0.0
    return bbox_poly.intersection(roi_poly).area / bbox_poly.union(roi_poly).area

def judge_slots(camera_id, image_path, roi_key):
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ 이미지 로드 실패: {image_path}")
        return []
    img_h, img_w = image.shape[:2]

    label_file = os.path.join(YOLO_LABEL_DIR, os.path.basename(image_path).replace(".jpg", ".txt"))
    bboxes = parse_yolo_result(label_file, img_w, img_h)

    results = []
    for roi in ROI_DATA[roi_key]:
        slot_id = roi["slot_id"]
        coords = roi["coords"]
        max_iou = max([calculate_iou(bbox, coords) for bbox in bboxes], default=0.0)
        status = "occupied" if max_iou >= 0.3 else "free"
        results.append({"slot_id": slot_id, "status": status})
    return results

def send_to_backend(camera_id, slot_results):
    payload = {
        "camera_id": camera_id,
        "timestamp": datetime.utcnow().isoformat(),
        "slots": slot_results
    }
    try:
        res = requests.post(API_ENDPOINT, headers=AUTH_HEADER, json=payload)
        print(f"[API] {camera_id}: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"[ERROR] API 전송 실패: {e}")

def run_pipeline():
    for cam_id, config in CAMERA_CONFIG.items():
        image_path = config["image_path"]
        roi_key = config["roi_key"]

        print(f"\n📷 {cam_id} 처리 시작")
        run_yolo(image_path)
        results = judge_slots(cam_id, image_path, roi_key)
        send_to_backend(cam_id, results)

# ✅ 반복 실행 예시 (3분 간격)
if __name__ == "__main__":
    while True:
        print(f"=== 🔁 판단 주기 시작: {datetime.now()} ===")
        run_pipeline()
        print(f"=== ⏱️ 3분 대기 ===")
        time.sleep(180)
