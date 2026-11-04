# ZooLens Architecture

Browser -> Laravel (Blade UI, factsheets, badge logic, SQLite for local development) -> FastAPI (image validation and inference) -> YOLO11n weights.

API contract: POST /predict multipart/form-data with field `file`; response `image_width`, `image_height`, `detections[]` with `class_name`, `confidence`, `bbox` in xyxy pixel coordinates.

This architecture is integrated and operational per Milestone 1 (W5):
- Frontend: Blade templates + Tailwind CDN with HTML5 Canvas bounding box rendering.
- Backend: Laravel 11 handling `/scan` multipart forwarding, session management, and `FactsheetService` database lookup.
- AI Service: FastAPI `/predict` endpoint loading YOLO11n weights (`best.pt`) with canonical English class mapping.
- Database: 4 tables (`animals`, `badges`, `user_animals`, `detections`) migrated and seeded.
