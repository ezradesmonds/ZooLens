# ZooLens Architecture

Browser -> Laravel (Blade UI, factsheets, badge logic, SQLite for local development) -> FastAPI (image validation and inference) -> YOLO11n weights.

API contract: POST /predict multipart/form-data with field `file`; response `image_width`, `image_height`, `detections[]` with `class_name`, `confidence`, `bbox` in xyxy pixel coordinates.

This is an initial scaffold, not a finished integration. Laravel calls, database migrations, UI screens, authorization, badge rules and trained model are pending work items.
