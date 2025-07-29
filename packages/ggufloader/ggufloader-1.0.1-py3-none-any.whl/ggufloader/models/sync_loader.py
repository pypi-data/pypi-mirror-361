# ggufloader/models/sync_loader.py

try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False

class SyncModelLoader:
    def __init__(self, model_path: str, use_gpu: bool = False, n_ctx: int = 512):
        if not LLAMA_AVAILABLE:
            raise ImportError("llama-cpp-python is not installed.")
        self.model_path = model_path
        self.use_gpu = use_gpu
        self.n_ctx = n_ctx
        self.model = None

    def load(self):
        n_gpu_layers = 20 if self.use_gpu else 0
        self.model = Llama(
            model_path=self.model_path,
            n_ctx=self.n_ctx,
            n_gpu_layers=n_gpu_layers,
            verbose=False
        )
        return self.model

    def chat(self, prompt: str) -> str:
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() first.")
        response = self.model(prompt)
        return response['choices'][0]['message']['content']
