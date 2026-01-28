"""Script para ejecutar el servidor en modo desarrollo"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=5003,
        reload=True,
        log_level="debug"
    )
