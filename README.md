# AI Vehicle Detection

## Overview

AI Vehicle Detection is a Flask web application that uses the YOLOv8 model to identify vehicles in uploaded images. It displays the original image, a processed image with bounding boxes, per-vehicle confidence scores, aggregate statistics, and a searchable detection history.

## Main Features

- YOLO detection for cars, motorcycles, buses, and trucks
- Bounding boxes and labels rendered on a processed image
- Confidence scores for each detected vehicle
- Total, per-type, and average-confidence statistics
- Drag-and-drop or file-browser image upload
- Client and server upload validation
- Collision-safe uploaded filenames
- Detection history saved locally in `backend/history.json`
- History search by filename, vehicle-type filters, and newest-first sorting
- Links to view both original and processed images
- Responsive layout for desktop and mobile screens

## Technology Stack

- Python and Flask
- Ultralytics YOLOv8
- OpenCV for image validation and processed output
- HTML, CSS, and vanilla JavaScript

## Project Structure

```text
AI-Vehicle-detection/
├── backend/
│   ├── app.py                 Flask routes and history persistence
│   ├── detector.py            YOLO detection and bounding boxes
│   └── uploads/               Uploaded and processed images
├── frontend/
│   ├── static/
│   │   ├── script.js          Upload, results, and history interactions
│   │   ├── style.css          Existing dashboard styles
│   │   └── assets/             UI image assets
│   └── templates/
│       └── index.html          Dashboard template
├── yolov8n.pt                 YOLO model weights
├── requirements.txt           Python dependencies
└── README.md
```

`backend/history.json` is created automatically after the first successful detection. It is local runtime data and is not required for a fresh installation.

## Installation and Setup

1. Create and activate a virtual environment:

	```powershell
	python -m venv .venv
	.\.venv\Scripts\Activate.ps1
	```

2. Install the pinned project dependency ranges:

	```powershell
	pip install -r requirements.txt
	```

3. Confirm that `yolov8n.pt` is present in the project root.

## Run Flask

From the project root, run:

```powershell
\.venv\Scripts\python.exe backend\app.py
```

Open <http://127.0.0.1:5000/> in a browser.

## Use Vehicle Detection

1. Choose an image with **Browse file** or drag it into the upload area.
2. Select a supported image: JPG, JPEG, PNG, BMP, or WEBP.
3. Keep the file at or below the 10 MB upload limit.
4. Select **Detect Vehicle**.
5. Review the original image, processed bounding-box image, detection cards, and statistics.
6. Use Detection History to search by filename, filter by vehicle type, and open the original or processed images.

The server sanitizes filenames, prevents collisions by adding a unique suffix, rejects unsupported extensions and invalid image data, and removes failed-upload files when processing fails.

## YOLO Detection and Output

The application loads `yolov8n.pt` through Ultralytics. It keeps the vehicle classes car, motorcycle, bus, and truck, converts confidence values to percentages, and writes labels and bounding boxes to a processed JPEG image.

For example, a vehicle image can produce output similar to:

```text
Total vehicles: 5
Cars: 4
Trucks: 1
Buses: 0
Motorcycles: 0
Average confidence: 59.86%
```

The exact result depends on the image and model output.

## Detection History

After a successful upload, the application stores the source filename, processed filename, UTC timestamp, and statistics in `backend/history.json`. The `/history` endpoint returns valid records whose files are safely named and available status is included for each image. Missing or malformed history data falls back to an empty history instead of stopping Flask.

## Future Improvements

- Optional persistent database storage for multi-user deployments
- Authentication and role-based access
- Configurable model selection and confidence thresholds
- Exportable history reports
- Live camera input
