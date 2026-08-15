"""
YOLOv8 + OpenCV — Real-time Object Detection
---------------------------------------------
Detects and labels ALL objects YOLOv8 recognizes (80 COCO classes)
from a webcam feed, video file, or single image.

Install dependencies first:
    pip install ultralytics opencv-python

Usage:
    python yolov8_object_detection.py                 # webcam (default)
    python yolov8_object_detection.py --source video.mp4
    python yolov8_object_detection.py --source image.jpg
    python yolov8_object_detection.py --model yolov8s.pt --conf 0.5
"""

import argparse
import cv2
from ultralytics import YOLO


def parse_args():
    parser = argparse.ArgumentParser(description="YOLOv8 + OpenCV Object Detection")
    parser.add_argument(
        "--source",
        type=str,
        default="0",
        help="Video source: '0' for webcam, or path to video/image file",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="yolov8n.pt",
        help="YOLOv8 model weights (yolov8n/s/m/l/x.pt). 'n' is fastest, 'x' is most accurate.",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.4,
        help="Confidence threshold for detections (0-1)",
    )
    parser.add_argument(
        "--save",
        type=str,
        default=None,
        help="Optional path to save the output video (e.g. output.mp4)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Load the YOLOv8 model (downloads automatically on first run)
    model = YOLO(args.model)

    # Webcam source is passed as an integer index, files as a string path
    source = int(args.source) if args.source.isdigit() else args.source
    cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        print(f"[ERROR] Could not open source: {args.source}")
        return

    # Optional: set up video writer if saving output
    writer = None
    if args.save:
        fps = cap.get(cv2.CAP_PROP_FPS) or 20
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(args.save, fourcc, fps, (width, height))

    print("Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[INFO] End of stream or failed to grab frame.")
            break

        # Run YOLOv8 inference on the frame — detects ALL object classes
        results = model(frame, conf=args.conf, verbose=False)

        # results[0].plot() draws boxes, labels, and confidence scores
        annotated_frame = results[0].plot()

        # Print detected object names + counts to the console
        if results[0].boxes is not None and len(results[0].boxes) > 0:
            names = model.names
            class_ids = results[0].boxes.cls.cpu().numpy().astype(int)
            detected_objects = [names[c] for c in class_ids]
            counts = {obj: detected_objects.count(obj) for obj in set(detected_objects)}
            summary = ", ".join(f"{v}x {k}" for k, v in counts.items())
            print(f"Detected: {summary}")

        cv2.imshow("YOLOv8 Object Detection", annotated_frame)

        if writer is not None:
            writer.write(annotated_frame)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    if writer is not None:
        writer.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
