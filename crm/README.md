# CRM Setup

## 1. Install Redis and Dependencies

### Install Redis

```bash
sudo apt update
sudo apt install redis-server
```


Start Redis and ensure it is running:
```bash
redis-server
```

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

## 2. Run Database Migrations

Apply Django migrations to set up the database schema:
```bash
python manage.py migrate
```

## 3. Start Celery Worker

In a new terminal session, start the Celery worker:
```bash
celery -A crm worker -l info
```

## 4. Start Celery Beat

In another terminal session, start Celery Beat for scheduled tasks:
```bash
celery -A crm beat -l info
```

## 5. Verify Logs

Confirm that reports and background tasks are logging correctly by checking the log file:
```bash
cat /tmp/crm_report_log.txt
```
