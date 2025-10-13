# Docker Configuration

Docker Compose setup for FastAPI backend and Label Studio.

## Setup

1. Copy environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your Firebase project details

3. Ensure Firebase credentials are in place:
```bash
cp /path/to/your/firebase-credentials.json ../backend/firebase-credentials.json
```

## Starting Services

Start all services:
```bash
docker-compose up -d
```

View logs:
```bash
docker-compose logs -f
```

## Services

- **FastAPI Backend**: http://localhost:8000
  - API docs: http://localhost:8000/docs
  - Health check: http://localhost:8000/api/health

- **Label Studio**: http://localhost:8080
  - Default credentials: Create account on first visit

## Stopping Services

```bash
docker-compose down
```

To remove volumes as well:
```bash
docker-compose down -v
```

## Label Studio Configuration

1. Access Label Studio at http://localhost:8080
2. Create an account
3. Create a new project for CT Tick annotations
4. Configure labeling interface for:
   - Bounding boxes (for YOLOv10 detection)
   - Polygon/brush segmentation (for MONAI training)

### Label Studio XML Config (Bounding Box):

```xml
<View>
  <Image name="image" value="$image"/>
  <RectangleLabels name="bbox" toName="image">
    <Label value="tick" background="red"/>
  </RectangleLabels>
</View>
```

### Label Studio XML Config (Segmentation):

```xml
<View>
  <Image name="image" value="$image"/>
  <BrushLabels name="mask" toName="image">
    <Label value="organ1" background="rgba(255,0,0,0.5)"/>
    <Label value="organ2" background="rgba(0,255,0,0.5)"/>
    <Label value="organ3" background="rgba(0,0,255,0.5)"/>
  </BrushLabels>
</View>
```

## Troubleshooting

### Port conflicts
If ports 8000 or 8080 are already in use, edit `docker-compose.yml` to change the port mappings.

### Firebase connection issues
Ensure `firebase-credentials.json` is valid and has the correct permissions.

