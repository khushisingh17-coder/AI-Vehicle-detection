from ultralytics import YOLO
import cv2

# Load YOLO model
model = YOLO("yolov8n.pt")


def detect_vehicles(image_path, processed_image_path=None):

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
                confidence_percent = round(confidence * 100, 2)

                detected_vehicles.append({
                    "vehicle": vehicle_name,
                    "confidence": confidence_percent
                })

                if processed_image_path:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
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