# Tourism Recommendation System

A Flask-based tourism recommendation system using TripAdvisor data with intelligent scoring algorithms and itinerary optimization.

## Features
- Smart recommendation engine with configurable scoring
- Multi-day itinerary optimization
- Weather integration
- Interactive UI with localStorage persistence
- Category-based filtering

## Local Development

### Prerequisites
- Python 3.11+
- pip or conda

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd tourism-recommender
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create .env file:
```bash
cp .env.example .env
# Edit .env and set your secret key
```

5. Run the app:
```bash
python app.py
```

Visit http://localhost:5000

## Deployment to Render

1. Push code to GitHub
2. Go to https://render.com
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Render will auto-detect settings from render.yaml
6. Click "Create Web Service"
7. Wait for deployment (3-5 minutes)

## Project Structure

```
tourism-recommender/
├── app.py                 # Main Flask application
├── config.py             # Configuration and scoring weights
├── recommender/          # Recommendation engine
│   ├── engine.py
│   ├── scoring.py
│   └── itinerary.py
├── services/             # External services
│   ├── data_loader.py
│   ├── weather_service.py
│   └── geocoding_service.py
├── templates/            # HTML templates
│   └── index.html
├── static/              # Static assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── data/                # Dataset
    └── tripadvisor_data.csv
```

## Technologies
- **Backend**: Flask, Python 3.11
- **Data**: Pandas
- **Caching**: Flask-Caching
- **APIs**: Open-Meteo (weather), Nominatim (geocoding)
- **Frontend**: Vanilla JavaScript, CSS3

## License
MIT