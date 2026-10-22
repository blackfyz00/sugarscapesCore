# src/server_entry.py
import sys
import argparse
from pathlib import Path

# Добавляем текущую директорию в path, чтобы импорты работали как в main.py
script_dir = Path(__file__).parent.resolve()
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from ai_chat_server import run_server

def parse_args():
    parser = argparse.ArgumentParser(description="Sugarscape AI Chat Server")
    parser.add_argument("--data", type=str, required=True, help="Path to .ai.json file")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    return parser.parse_args()

def main():
    args = parse_args()
    
    data_path = Path(args.data)
    if not data_path.exists():
        print(f"❌ Error: Data file not found: {data_path}", file=sys.stderr)
        sys.exit(1)
        
    print(f"🚀 Starting AI Server for {data_path.name} on port {args.port}...")
    
    try:
        # Запускаем блокирующий цикл uvicorn
        run_server(str(data_path), args.port)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Critical error starting server: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()