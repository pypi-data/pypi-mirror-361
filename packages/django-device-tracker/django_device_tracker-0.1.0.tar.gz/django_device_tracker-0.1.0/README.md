A reusable Django app for tracking user login devices securely. Plug it into any Django project and monitor user sessions, IPs, and browser info.

## Features
- Tracks IP address and browser info (User-Agent)
- Stores refresh token JTI
- View and manage user devices via admin
- Designed to be plug-and-play

## Installation
```bash
pip install django-device-tracker
```

## Usage
1. Add to `INSTALLED_APPS`:
```python
INSTALLED_APPS += ["device_tracker"]
```
2. Run migrations:
```bash
python manage.py migrate device_tracker
```
3. Use in your views:
```python
from device_tracker.utils import track_device

track_device(request, user, refresh_token)
```

## License
MIT