# Django Device Tracker

A reusable Django app to track user login devices — plug-and-play for any Django project using session or JWT-based authentication.

---

## 🔧 Features

- Track IP address and user-agent per login
- Compatible with JWT (e.g., simplejwt)
- Saves login timestamp and refresh token `jti`
- Admin panel support
- Lightweight, no external dependencies

---

## 📦 Installation

```bash
pip install django-device-tracker
```

Add to your `INSTALLED_APPS`:
```python
INSTALLED_APPS += ["device_tracker"]
```

Apply migrations:
```bash
python manage.py migrate device_tracker
```

---

## 🚀 Usage

### Manual tracking per login (JWT):

In your login/signup/OTP views:
```python
from device_tracker.utils import track_device

# After creating refresh token:
track_device(request, user, refresh_token)
```

The `refresh_token` is optional but strongly recommended for managing sessions.

### What it stores:
- `user`: ForeignKey to your user model
- `ip_address`: Auto-resolved from request headers
- `device_name`: User-Agent header
- `refresh_token_jti`: Extracted from token if provided
- `last_seen`: Timestamp of login
- `is_active`: Boolean flag (you can control this)

---

## 🛠 Admin Support

Device tracking entries are available in Django admin under `Device` model.

---

## 🔍 Advanced Integration Ideas (Optional)

- Custom middleware to track every request or session
- Show user active devices (build your own API/view)
- Revoke session by removing device entry or blacklisting token

---

## 📂 Development

To install locally:
```bash
git clone https://github.com/yourusername/django-device-tracker.git
cd django-device-tracker
pip install -e .
```

---

## 🪪 License

MIT License. See `LICENSE` file.

---

## ✍️ Author

Developed by [mejomba]. Contributions and feedback welcome!
