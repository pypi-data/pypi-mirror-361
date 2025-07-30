# ggufloader/__init__.py

from ggufloader.models.sync_loader import SyncModelLoader

_model_instance = None

def _get_model():
    global _model_instance
    if _model_instance is None:
        # Adjust default model path and settings as needed
        _model_instance = SyncModelLoader("models/mistral.gguf", use_gpu=False)
        _model_instance.load()
    return _model_instance

def chat(prompt: str) -> str:
    model = _get_model()
    return model.chat(prompt)
