# ML Price Prediction - Django

Self-updating price prediction service with a daily retraining job and a simple web UI.

## Features
- REST API: `POST /api/predict/` predicts price from input features
- Web UI: `/api/` page to enter inputs and see prediction
- Daily retraining at 00:00 using `django-crontab` and synthetic data augmentation
- Artifacts stored under `artifacts/` and dataset under `data/`

## Requirements
- Python 3.13+
- System packages: `python3-venv`, `python3-dev`, `build-essential`, `cron`

## Setup
```bash
# From the mlproject directory
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py retrain_model --rows 1000
```

## Run Server
```bash
python manage.py runserver 0.0.0.0:8000
```
- Web UI: `http://localhost:8000/api/`
- API: `http://localhost:8000/api/predict/`

### Example Request
```bash
curl -s -X POST http://localhost:8000/api/predict/ \
  -H 'Content-Type: application/json' \
  -d '{"size": 100, "bedrooms": 3, "bathrooms": 2, "age": 10}'
```

## Scheduling (Daily Retrain)
We use `django-crontab` to retrain the model daily at 00:00.

```bash
# Ensure cron service is running
sudo service cron start

# Register the job
python manage.py crontab add

# List jobs
python manage.py crontab show
```

Manual retrain:
```bash
python manage.py retrain_model --rows 500
```

## Project Structure
```
mlproject/
  manage.py
  mlproject/
    settings.py
    urls.py
  prices/
    ml.py
    views.py
    urls.py
    management/commands/retrain_model.py
  templates/prices/predict.html
  data/
  artifacts/
requirements.txt
README.md
```

## Notes
- The dataset is synthesized and extended on each retrain to simulate “latest data”. Replace `augment_dataset_with_synthetic` in `prices/ml.py` with real ingestion as needed.
- To change the schedule, edit `CRONJOBS` in `mlproject/settings.py`.