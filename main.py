from fastapi import FastAPI
import uvicorn
from endpoint.user_endpoint import router as user_router
from endpoint.auth_endpoint import router as auth_router
from endpoint.job_description_endpoint import router as jd_router
from endpoint.resume_endpoint import router as rs_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(jd_router)
app.include_router(rs_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 