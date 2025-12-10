try:
    from asgiref.wsgi import ASGItoWSGI as Adapter
except ImportError:
    from asgiref.wsgi import AsgiToWsgi as Adapter
from main import app as fastapi_app

app = Adapter(fastapi_app)
