# WORKOUTWITHAI

## Video Analysis and Enhancement Platform with AI

This project leverages deep learning models to analyze workout videos, provide form feedback, and enhance video quality. It combines video analysis, pose estimation, and personalized feedback to create an interactive AI-powered workout companion.

## Key Features

- Real-time pose detection and form analysis
- Custom-trained transformer models for workout movement recognition
- Automated feedback generation for proper exercise form
- Video enhancement capabilities for improved visual quality
- Interactive web interface for uploading and analyzing workout videos
- API endpoints for integration with mobile apps and other platforms

## Technology Stack

- **Backend**: Python, FastAPI
- **Machine Learning**: PyTorch, TimeSformer, Transformers
- **Video Processing**: OpenCV, FFMPEG
- **Frontend**: HTML/CSS/JavaScript, Gradio
- **Deployment**: Docker, Kubernetes
- **Database**: SQLAlchemy

## Getting Started

### Prerequisites

- Python 3.8+
- CUDA-compatible GPU (recommended for optimal performance)
- Docker and Docker Compose (for containerized deployment)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements_ml_video.txt
   ```
3. Start the application:
   ```bash
   bash run.sh
   ```

Alternatively, use Docker:
```bash
docker-compose up -d
```

## Usage

1. Access the web interface at `http://localhost:8000`
2. Upload a workout video
3. Select analysis options
4. View the results and feedback

## API Documentation

See [api_documentation.md](api_documentation.md) for details on available endpoints.

## Deployment

For production deployment instructions, refer to [deployment_guide.md](deployment_guide.md).

## Project Structure

- `app.py`: Main application entry point
- `main.py`: FastAPI application setup
- `video_analysis.py`: Core video analysis functionality
- `transformer_models.py`: Custom transformer models for video analysis
- `enhanced_video_analyzer.py`: Advanced video enhancement capabilities
- `fine_tune_timesformer.py`: Training scripts for TimeSformer model
- `database/`: Database models and connection handlers
- `static/`: Static assets for the web interface
- `kubernetes.yml`: Kubernetes deployment configuration

## License

MIT 