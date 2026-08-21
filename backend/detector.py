from ultralytics import YOLO
import cv2
import os

# Load YOLO model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "yolov8n.pt")
model = YOLO(MODEL_PATH)
VEHICLE_CONFIDENCE_THRESHOLD = 0.30


def estimate_vehicle_color(image, bbox):
    image_height, image_width = image.shape[:2]
    x1, y1, x2, y2 = [int(value) for value in bbox]
    x1 = max(0, min(x1, image_width))
    y1 = max(0, min(y1, image_height))
    x2 = max(0, min(x2, image_width))
    y2 = max(0, min(y2, image_height))

    if x2 <= x1 or y2 <= y1 or (x2 - x1) < 20 or (y2 - y1) < 20:
        return "Unknown"

    crop = image[y1:y2, x1:x2]
    crop_height, crop_width = crop.shape[:2]
    margin_x = max(1, int(crop_width * 0.15))
    margin_y = max(1, int(crop_height * 0.15))
    crop = crop[margin_y:crop_height - margin_y, margin_x:crop_width - margin_x]

    if crop.size == 0:
        return "Unknown"

    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    pixels = hsv.reshape(-1, 3)
    saturation = pixels[:, 1]
    value = pixels[:, 2]
    valid_pixels = pixels

    if len(valid_pixels) < max(20, int(len(pixels) * 0.15)):
        return "Unknown"

    neutral_pixels = valid_pixels[valid_pixels[:, 1] < 55]
    if len(neutral_pixels) >= len(valid_pixels) * 0.55:
        mean_value = float(neutral_pixels[:, 2].mean())
        value_spread = float(neutral_pixels[:, 2].std())
        if mean_value < 70:
            return "Black"
        if mean_value > 185 and value_spread < 55:
            return "White"
        if value_spread < 65:
            return "Grey" if mean_value < 165 else "Silver"
        return "Unknown"

    colored_pixels = valid_pixels[valid_pixels[:, 1] >= 55]
    if len(colored_pixels) < len(valid_pixels) * 0.2:
        return "Unknown"

    hue_histogram = cv2.calcHist([colored_pixels[:, 0]], [0], None, [180], [0, 180]).flatten()
    dominant_hue = int(hue_histogram.argmax())
    dominant_ratio = float(hue_histogram[dominant_hue] / len(colored_pixels))
    if dominant_ratio < 0.28:
        return "Unknown"
    if dominant_hue < 10 or dominant_hue >= 170:
        return "Red"
    if dominant_hue < 22:
        return "Orange"
    if dominant_hue < 38:
        return "Yellow"
    if dominant_hue < 85:
        return "Green"
    if dominant_hue < 135:
        return "Blue"
    return "Unknown"


def detect_vehicles(image_path, processed_image_path=None):

    image = cv2.imread(image_path)

    if image is None:
        return []

    results = model(image, conf=VEHICLE_CONFIDENCE_THRESHOLD)

    detected_vehicles = []

    vehicle_classes = {
        2: "car",
        3: "motorcycle",
        5: "bus",
        7: "truck"
    }

    for result in results:

        boxes = result.boxes

        for box in boxes:

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            if class_id in vehicle_classes and confidence >= VEHICLE_CONFIDENCE_THRESHOLD:

                vehicle_name = vehicle_classes[class_id]
                confidence_percent = round(confidence * 100, 2)
                bbox = [int(value) for value in box.xyxy[0].tolist()]

                detected_vehicles.append({
                    "vehicle": vehicle_name,
                    "confidence": confidence_percent,
                    "bbox": bbox,
                    "color": estimate_vehicle_color(image, bbox),
                    "plate": "Not available",
                    "plate_confidence": 0,
                    "state": "Unknown",
                    "registration_region": "Not available",
                    "brand": "Unknown",
                    "model": "Unknown",
                    "plate_bbox": None
                })

                if processed_image_path:
                    x1, y1, x2, y2 = bbox
                    label = f"{vehicle_name} {confidence_percent:.2f}%"
                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 200, 255), 2)
                    label_y = max(y1 - 10, 20)
                    cv2.putText(
                        image,
                        label,
                        (x1, label_y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 200, 255),
                        2,
                        cv2.LINE_AA
                    )

    if processed_image_path and not cv2.imwrite(processed_image_path, image):
        raise OSError("Unable to save processed image")

    return detected_vehicles