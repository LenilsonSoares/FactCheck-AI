from app.services.google_api import GoogleFactCheckClient


class GoogleFactCheckProvider(GoogleFactCheckClient):
    """Adapter para manter compatibilidade do cliente atual com os ports da aplicação."""

