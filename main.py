from fastapi import FastAPI
import uvicorn
from endpoint.user_endpoint import router as user_router
from endpoint.auth_endpoint import router as auth_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)