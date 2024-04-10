from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes
from langchain_google_vertexai import VertexAI
from langchain_core.output_parsers import StrOutputParser

app = FastAPI()
llm = VertexAI(model_name="gemini-1.0-pro-001")
chain = (llm | StrOutputParser())

@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


# Edit this to add the chain you want to add
add_routes(app, chain)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
