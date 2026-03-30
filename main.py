import os
import jwt
from fastapi import Request, FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from config import settings
from func import tag_and_answer, tag_only, tag_and_answer_SINGLE

# Configuración de OpenAI
OPENAI_KEY = settings.OPENAI_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_KEY
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"

app = FastAPI()

# Ruta de salud
@app.get("/healthz", status_code=200)
def healthz():
    return {"status": "ok"}

# Ruta /tag con autenticación
@app.post("/tag")
async def tag_endpoint(request: Request):
    
    try:
        req = await request.json()
        text = req.get("text")
        client = req.get("client")
        ignore = req.get("ignore")
        derive = req.get("derive")

        if not text:
            return JSONResponse(content={"error": "Falta la clave 'text' en el cuerpo de la solicitud"}, status_code=400)
        if not client:
            return JSONResponse(content={"error": "Falta la clave 'client' en el cuerpo de la solicitud"}, status_code=400)
        
        response_json = await tag_and_answer(text, client, ignore=ignore, derive=derive)
        return JSONResponse(content=response_json, status_code=200)

    except ValueError:
        return JSONResponse(content={"error": "El cuerpo de la solicitud no es JSON válido"}, status_code=400)
    except Exception as e:
        print("Error interno:", {str(e)})
        return JSONResponse(content={"error": f"Error interno: {str(e)}"}, status_code=500)

# Ruta /tag_only con autenticación
@app.post("/tag_only")
async def tag_only_endpoint(request: Request):
    
    try:
        req = await request.json()
        text = req.get("text")
        client = req.get("client")
        
        if not text:
            return JSONResponse(content={"error": "Falta la clave 'text' en el cuerpo de la solicitud"}, status_code=400)
        if not client:  
            return JSONResponse(content={"error": "Falta la clave 'client' en el cuerpo de la solicitud"}, status_code=400)
        
        response_json = await tag_only(text, client)
        return JSONResponse(content=response_json, status_code=200)

    except ValueError:
        return JSONResponse(content={"error": "El cuerpo de la solicitud no es JSON válido"}, status_code=400)
    except Exception as e:
        print("Error interno:", {str(e)})
        return JSONResponse(content={"error": f"Error interno: {str(e)}"}, status_code=500)
    
    
    # Ruta /tag con autenticación
@app.post("/tag_single")
async def tag_endpoint(request: Request, authorization: str = Header(None)):
    
    try:
        req = await request.json()
        text = req.get("text")
        client = req.get("client")
        ignore = req.get("ignore")
        derive = req.get("derive")

        if not text:
            return JSONResponse(content={"error": "Falta la clave 'text' en el cuerpo de la solicitud"}, status_code=400)
        if not client:
            return JSONResponse(content={"error": "Falta la clave 'client' en el cuerpo de la solicitud"}, status_code=400)
        
        response_json = await tag_and_answer_SINGLE(text, client, ignore=ignore, derive=derive)
        return JSONResponse(content=response_json, status_code=200)

    except ValueError:
        return JSONResponse(content={"error": "El cuerpo de la solicitud no es JSON válido"}, status_code=400)
    except Exception as e:
        print("Error interno:", {str(e)})
        return JSONResponse(content={"error": f"Error interno: {str(e)}"}, status_code=500)
