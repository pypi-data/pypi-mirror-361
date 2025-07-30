# GGUF Loader
![License](https://img.shields.io/github/license/ggufloader/gguf-loader)
![Last Commit](https://img.shields.io/github/last-commit/ggufloader/gguf-loader)
![Repo Size](https://img.shields.io/github/repo-size/ggufloader/gguf-loader)
![Issues](https://img.shields.io/github/issues/ggufloader/gguf-loader)

Easiest way to run and manage GGUF-based LLMs locally — with drag-and-drop GUI, plugin system, and zero terminal setup.

## 🚀 Install in One Line

```bash
pip install ggufloader
```

```bash
ggufloader
```

Works on Windows, Linux, and macOS.

## 🌟 Why GGUF Loader?

- ✅ No terminal needed — fully GUI-based  
- 🔌 Blender-style plugin system for custom tools  
- 🧠 Built for local LLMs: Mistral, LLaMA, DeepSeek, etc.  
- ⚡ Runs even on Intel i5 + 16GB RAM  
- 📁 Drag and drop `.gguf` models and run  

> Ideal for beginners, researchers, or anyone avoiding cloud APIs.

## 🖼️ Preview
![Image 1](https://raw.githubusercontent.com/GGUFloader/gguf-loader/main/1.png)  
![Image 2](https://raw.githubusercontent.com/GGUFloader/gguf-loader/main/2.png)

## 📦 Features

| Feature                 | Description                                     |
|------------------------|-------------------------------------------------|
| GUI for GGUF LLMs      | Run models without terminal or coding          |
| Addon System           | Extend with plugins like summarizers, exporters |
| Cross-platform Support | Windows / Linux / macOS                        |
| Multi-Model Friendly   | Mistral, LLaMA, DeepSeek, Yi, Gemma, OpenHermes |
| Memory-Efficient       | Works on low-spec laptops (16GB RAM)           |

## 📘 How It Works

1. Install via `pip install ggufloader`  
2. Launch it with `ggufloader`  
3. Drag and drop your `.gguf` models  
4. Start chatting with local LLMs instantly  
5. Add features via plugins (like PDF, email, spreadsheet)

## ⚙️ Advanced Usage

- Run via CLI: `ggufloader --model mistral.gguf`  
- Use Addon: `ggufloader --addon summarize_pdf`  
- Import in Python:

```python
from ggufloader import chat
chat("Hello, local world!")
```

## 🧠 Use Cases

- Run LLaMA 3 or Mistral on your own machine  
- Build your own local ChatGPT  
- Summarize documents with AI locally  
- Run AI completely offline (no API needed)

> *Perfect for local-first AI, privacy-focused developers, and automation hackers.*

## 💡 Comparison with Similar Tools

| Tool           | GUI | Addons | Pip Install | Offline Use | Notes                          |
|----------------|-----|--------|-------------|-------------|-------------------------------|
| GGUF Loader ✅  | ✅  | ✅     | ✅          | ✅          | Modular, privacy-first         |
| LM Studio      | ✅  | ❌     | ❌          | ✅          | More polished, less flexible   |
| Ollama         | ❌  | ❌     | ❌          | ✅          | CLI-first, tightly scoped      |
| GPT4All        | ✅  | ❌     | ✅          | ✅          | Limited extension support      |

## 📎 Links

- 🏠 Website: [ggufloader.github.io](https://ggufloader.github.io)  
- 🧪 PyPI: [https://pypi.org/project/ggufloader](https://pypi.org/project/ggufloader)
- 📂 GitHub: [github.com/ggufloader/ggufloader](https://github.com/ggufloader/ggufloader)

## ❓ FAQ

**Q: What is GGUF?**  
A new file format for optimized local LLM models (used in llama.cpp, Mistral, etc).

**Q: Can I use it offline?**  
Yes — GGUF Loader runs completely offline and doesn’t use OpenAI or API calls.

**Q: Does it support plugins?**  
Yes! Use addons for PDF reading, summarization, chatbot modes, spreadsheet processing, and more.

