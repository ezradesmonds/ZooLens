import io
from fastapi.testclient import TestClient
from PIL import Image
from app.main import app

client = TestClient(app)


def test_predict_endpoint_success():
    # Create a dummy image
    img = Image.new("RGB", (320, 320), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    response = client.post("/predict", files={"file": ("test.jpg", buf, "image/jpeg")})
    assert response.status_code == 200
    data = response.json()
    assert "image_width" in data
    assert "image_height" in data
    assert "detections" in data
    assert data["image_width"] == 320
    assert data["image_height"] == 320


def test_predict_invalid_file_type():
    buf = io.BytesIO(b"not an image")
    response = client.post("/predict", files={"file": ("test.txt", buf, "text/plain")})
    assert response.status_code == 415
