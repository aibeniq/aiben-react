from app.services.vectordb.main import VectorDBService


class AppState:
    vector_db_service: VectorDBService | None = None


app_state = AppState()
