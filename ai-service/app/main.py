from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import io
import os

app = FastAPI(title="ZooLens Inference API", version="0.1.0")

class Detection(BaseModel):
    class_name: str
    confidence: float
    bbox: list[float]

@app.get('/health')
def health():
    return {"status": "ok", "service": "zoolens-ai", "model_configured": bool(os.getenv('MODEL_PATH'))}

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
    model_path = os.getenv('MODEL_PATH', '')
    if not model_path or not os.path.isfile(model_path):
        raise HTTPException(status_code=503, detail='Model not installed. Set MODEL_PATH to YOLO weights.')
    from ultralytics import YOLO
    model = YOLO(model_path)
    result = model.predict(source=image, verbose=False)[0]
    detections = []
    for box in result.boxes:
        detections.append({
            'class_name': result.names[int(box.cls[0])],
            'confidence': round(float(box.conf[0]), 4),
            'bbox': [round(float(v), 2) for v in box.xyxy[0].tolist()],
        })
    return {'image_width': image.width, 'image_height': image.height, 'detections': detections}
