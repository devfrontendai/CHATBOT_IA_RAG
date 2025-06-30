# Chatbot RAG con FastAPI, Ollama y LlamaIndex

## 🚀 Descripción
Chatbot API que responde preguntas sobre productos, planes y coberturas usando **RAG** (Retrieval Augmented Generation) con FastAPI, Ollama y LlamaIndex. 
La base de productos puede ser masiva (20,000+ líneas).

---

## 📝 **Requisitos**
- Python 3.10+
- Dependencias de `requirements.txt` (incluye llama-index, fastapi, uvicorn, langchain, sentence-transformers, etc.)
- Docker y Docker Compose (recomendado para Ollama y API en producción)
- Carpeta `info/` con el archivo `productos.json`

---

## ⚙️ **Primer uso: Construir el índice vectorial (solo una vez o cuando cambies productos)**
1. Coloca tu archivo `productos.json` en la carpeta `info/`.
2. Asegúrate de tener todos los scripts:  
   - `build_index.py`  
   - `producto_loader.py`  
   - `rag_engine.py`
3. Abre una terminal en la carpeta donde están esos archivos.
4. Instala dependencias:
    ```bash
    pip install -r requirements.txt
    ```
5. Ejecuta:
    ```bash
    python build_index.py
    ```
   - Esto puede tardar varios minutos (¡es normal!).
   - Al terminar, verás la carpeta `storage/` generada.

---

## 🏁 **Arrancar la API con Docker Compose**

1. **(Si no tienes ya el index)**  
   Corre primero el build como se indica arriba.

2. Levanta todo con Docker:
    ```bash
    docker compose up --build
    ```

3. Abre en el navegador:  
    ```
    http://localhost:8000/docs
    ```
    Prueba el endpoint `/preguntar`.

---

## 🛠️ **Actualizar el índice**
Cada vez que cambies masivamente tu base de productos:
- Vuelve a correr:
    ```bash
    python build_index.py
    ```
- ¡No necesitas reiniciar todo el API, solo recargar el índice!

---

## ⚡️ **Tips Pro**
- **No borres la carpeta `storage/`**, ahí está tu índice listo para cargar rápido.
- **Para desarrollo, prueba con un archivo pequeño de productos antes de hacer el build grande.**
- Si usas Docker en producción, monta la carpeta `storage/` como un volumen para persistencia real.

Ejemplo en `docker-compose.yml`:

```yaml
services:
  fastapi:
    volumes:
      - ./storage:/src/storage
      ...
