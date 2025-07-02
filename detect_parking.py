import sys
from pathlib import Path
import torch
import cv2
import json
import numpy as np

# 경로 설정
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # yolov5 디렉토리
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from models.experimental import attempt_load
from utils.datasets import LoadImages
from utils.general import check_img_size, non_max_suppression, scale_coords, set_logging
from utils.torch_utils import select_device

# ROI 정보 로드
with open('./roi_slots.json', 'r') as f:
    roi_dict = json.load(f)

image_path = "./images/datasets/campus/images/train/IMG_6857.JPG"
model_path = "./runs/train/exp6/weights/best.pt"

# 디바이스 설정
device = select_device('')
model = attempt_load(model_path, map_location=device)
stride = int(model.stride.max())
imgsz = check_img_size(640, s=stride)

# 이미지 로드 및 전처리
original_img = cv2.imread(image_path)
img = cv2.resize(original_img, (imgsz, imgsz))
img_tensor = torch.from_numpy(img).permute(2, 0, 1).float() / 255.0
img_tensor = img_tensor.unsqueeze(0).to(device)

# 추론
set_logging()
pred = model(img_tensor, augment=False)[0]
pred = non_max_suppression(pred, conf_thres=0.25, iou_thres=0.45)[0]

# 결과 좌표 원본 이미지 크기로 복원
pred = scale_coords(img_tensor.shape[2:], pred[:, :4], original_img.shape).round()

# 슬롯 상태 판단
for slot_id, points in roi_dict.items():
    pts = np.array(points, dtype=np.int32)
    roi_mask = np.zeros(original_img.shape[:2], dtype=np.uint8)
    cv2.fillPoly(roi_mask, [pts], 255)
    slot_img = cv2.bitwise_and(original_img, original_img, mask=roi_mask)

    # ROI 내부 객체 유무 판단
    occupied = False
    for *xyxy, conf, cls in pred:
        x1, y1, x2, y2 = map(int, xyxy)
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        if roi_mask[cy, cx] > 0:
            occupied = True
            break

    color = (0, 0, 255) if occupied else (0, 255, 0)
    label = "Occupied" if occupied else "Free"
    cv2.polylines(original_img, [pts], isClosed=True, color=color, thickness=2)
    cv2.putText(original_img, f"{slot_id}: {label}", tuple(pts[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

# 시각화
cv2.imshow("Result", original_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
