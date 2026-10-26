import io
import os
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel
from ultralytics import YOLO

load_dotenv()

app = FastAPI(title="ZooLens Inference API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ZOOLENS_CLASSES = {
    "elephant": 0,
    "giraffe": 1,
    "zebra": 2,
    "tiger": 3,
    "rhinoceros": 4,
}

_model = None


def get_model():
    global _model
    if _model is not None:
        return _model

    model_path = os.getenv("MODEL_PATH", "yolo11n.pt")
    if not os.path.isabs(model_path):
        possible_paths = [
            model_path,
            os.path.join(os.path.dirname(__file__), "..", model_path),
            os.path.join(os.path.dirname(__file__), "..", "..", model_path),
        ]
        for p in possible_paths:
            if os.path.isfile(p):
                model_path = p
                break

    if not os.path.isfile(model_path):
        return None

    _model = YOLO(model_path)
    return _model


class Detection(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: list[float]


@app.get('/health')
def health():
    model = get_model()
    model_path = os.getenv('MODEL_PATH', 'yolo11n.pt')
    return {
        "status": "ok",
        "service": "zoolens-ai",
        "model_configured": model is not None,
        "model_path": model_path if model is not None else None,
    }


@app.post('/predict')
async def predict(file: UploadFile = File(...)):
    if file.content_type not in ('image/jpeg', 'image/png', 'image/webp'):
        raise HTTPException(status_code=415, detail='JPEG, PNG, or WEBP required')
    data = await file.read(10 * 1024 * 1024 + 1)
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail='Image exceeds 10 MB')
    try:
        image = Image.open(io.BytesIO(data)).convert('RGB')
    except Exception:
        raise HTTPException(status_code=400, detail='Invalid image')

    model = get_model()
    if model is None:
        raise HTTPException(status_code=503, detail='Model not installed. Set MODEL_PATH to YOLO weights.')

    result = model.predict(source=image, verbose=False)[0]
    detections = []
    for box in result.boxes:
        raw_cls = int(box.cls[0])
        class_name = result.names[raw_cls].lower()

        # Map to ZooLens class_id (0..4)
        if len(result.names) == 5 and raw_cls in range(5):
            class_id = raw_cls
        elif class_name in ZOOLENS_CLASSES:
            class_id = ZOOLENS_CLASSES[class_name]
        else:
            continue

        detections.append({
            'class_id': class_id,
            'class_name': class_name,
            'confidence': round(float(box.conf[0]), 4),
            'bbox': [round(float(v), 2) for v in box.xyxy[0].tolist()],
        })
    return {'image_width': image.width, 'image_height': image.height, 'detections': detections}
