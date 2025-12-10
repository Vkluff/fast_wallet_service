from asgiref.wsgi import AsgiToWsgi
from main import app as fastapi_app

# Expose a WSGI-compatible app for Vercel's Python runtime
app = AsgiToWsgi(fastapi_app)
