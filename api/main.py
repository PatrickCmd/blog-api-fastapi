from fastapi import FastAPI

from .routes import auth, blog, password_reset, users

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(password_reset.router)
app.include_router(blog.router)
