"""Train only after verifying dataset licenses, annotations and splits.
Run: python ml/scripts/train.py --data ml/configs/dataset.yaml --epochs 50
"""
import argparse
from ultralytics import YOLO

parser = argparse.ArgumentParser()
parser.add_argument('--data', required=True)
parser.add_argument('--epochs', type=int, default=50)
args = parser.parse_args()
YOLO('yolo11n.pt').train(data=args.data, epochs=args.epochs, imgsz=640, project='ml/runs', name='zoolens')
