from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contacts_api.routes import contacts, auth, users
from contacts_api.conf.config import settings

import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter

app = FastAPI()

origins = ['http://localhost:8000']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')
app.include_router(users.router, prefix='/api')

@app.on_event('startup')
async def startup():
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding='utf-8', decode_responses=True)
    await FastAPILimiter.init(r)
    
@app.get('/')
def read_root():
    return {'message': 'Hello World'}