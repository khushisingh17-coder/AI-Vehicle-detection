from ultralytics import YOLO
import cv2

# Load YOLO model
model = YOLO("yolov8n.pt")


def detect_vehicles(image_path):

    image = cv2.imread(image_path)

    if image is None:
        return []

    results = model(image)

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

            if class_id in vehicle_classes:

                vehicle_name = vehicle_classes[class_id]

                detected_vehicles.append({
                    "vehicle": vehicle_name,
                    "confidence": round(confidence * 100, 2)
                })

    return detected_vehicles