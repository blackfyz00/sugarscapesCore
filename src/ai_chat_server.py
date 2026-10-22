import sys
import json
import os
from pathlib import Path
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

try:
    from dotenv import load_dotenv
    
    # Правильное определение папки для EXE и для скрипта
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys.executable).parent
    else:
        base_dir = Path(__file__).parent.parent
        
    env_path = base_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not installed.")

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None

app = FastAPI(title="Sugarscape AI Analyst")

STATE = {
    "summaries": [],
    "trend": [],
    "config": {},
    "html_path": ""
}

class ChatRequest(BaseModel):
    message: str

@app.get("/health")
async def health_check():
    return {"status": "ok", "loaded": bool(STATE["summaries"])}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            request_data = json.loads(data)
            user_message = request_data.get("message", "").strip()
            
            if not user_message:
                continue
                
            # Формируем контекст из последних шагов
            recent_summaries = "\n\n".join(STATE["summaries"][-15:]) 
            
            # Системный промпт БЕЗ вопроса пользователя
            system_prompt = f"""
            Ты эксперт-аналитик агентной модели Sugarscape.
            Отвечай на русском языке кратко и по делу.
            
            ДАННЫЕ СИМУЛЯЦИИ (последние шаги):
            {recent_summaries}
            
            ОБЩИЕ МЕТРИКИ:
            Конфиг: {json.dumps(STATE['config'], ensure_ascii=False)[:500]}...
            Тренд популяции: {STATE['trend'][-5:] if STATE['trend'] else 'Нет данных'}
            """
            
            api_key = os.getenv("OPENAI_API_KEY")
            base_url = os.getenv("APINET_BASE_URL")
            
            if not api_key or not OPENAI_AVAILABLE:
                await websocket.send_text("[ERROR] OPENAI_API_KEY не установлен или библиотека openai отсутствует.")
                continue

            client = AsyncOpenAI(
                api_key=api_key,
                base_url=base_url
            )
            
            try:
                # ИСПРАВЛЕНИЕ: Разделяем System и User сообщения
                response_stream = await client.chat.completions.create(
                    model="gemini-2.5-flash-lite",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message} # <--- Ключевое изменение
                    ],
                    stream=True
                )
                
                async for chunk in response_stream:
                    # Защита от пустых chunks
                    if not chunk.choices:
                        continue
                        
                    delta = chunk.choices[0].delta.content
                    if delta:
                        await websocket.send_text(delta)
                
                await websocket.send_text("[DONE]")
                
            except Exception as llm_err:
                import traceback
                err_str = str(llm_err)
                print(f"LLM Error: {err_str}") # Логируем на сервере
                # Отправляем понятную ошибку клиенту
                await websocket.send_text(f"[ERROR] Ошибка LLM: {err_str}")

    except Exception as e:
        print(f"WS Connection closed/error: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass

@app.get("/")
async def serve_dashboard():
    if STATE["html_path"] and Path(STATE["html_path"]).exists():
        return FileResponse(STATE["html_path"])
    raise HTTPException(status_code=404, detail="Dashboard HTML not found")

def load_context(json_path: str):
    """Загружает данные из .ai.json в память."""
    import sys
    path = Path(json_path)
    
    print(f"🔍 DEBUG: Loading context from: {path}")
    print(f"📂 Folder contents:")
    try:
        for f in path.parent.iterdir():
            print(f"   - {f.name} ({f.stat().st_size} bytes)")
    except Exception as e:
        print(f"   Error listing folder: {e}")

    if not path.exists():
        raise FileNotFoundError(f"Context file missing: {path}")
        
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    STATE["summaries"] = data.get("summaries", [])
    STATE["trend"] = data.get("trend", [])
    STATE["config"] = data.get("config", {})
    
    # --- АГРЕССИВНЫЙ ПОИСК HTML ---
    html_found = False
    
    # 1. Стандартный путь (.ai.json -> .html)
    candidate_standard = path.with_suffix('.html')
    print(f"🔎 Trying standard path: {candidate_standard}")
    if candidate_standard.exists():
        STATE["html_path"] = str(candidate_standard.resolve())
        print(f"✅ FOUND dashboard at standard path!")
        html_found = True
        
    # 2. Поиск по маске *.html в той же папке
    if not html_found:
        print(f"🔎 Standard failed. Searching for any .html in {path.parent}...")
        all_htmls = list(path.parent.glob("*.html"))
        if all_htmls:
            chosen = all_htmls[0]
            STATE["html_path"] = str(chosen.resolve())
            print(f"✅ FOUND dashboard via glob: {chosen.name}")
            html_found = True
            
    # 3. Если ничего не нашли
    if not html_found:
        print(f"❌ CRITICAL: NO HTML FILE FOUND IN FOLDER!")
        STATE["html_path"] = "" 

def run_server(data_path: str, port: int):
    load_context(data_path)
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")