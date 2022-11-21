import os
from typing import Union

from bson import ObjectId
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseModel, EmailStr, Field

# load env
load_dotenv()
MONGODB_URI = os.environ.get("MONGODB_URI")

client = AsyncIOMotorClient(MONGODB_URI)
db = client["blog_api"]


# BSON and fastapi JSON
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        allowed_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "johndoe@example.com",
                "password": "secret_code",
            }
        }


class Login(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        allowed_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "email": "johndoe@example.com",
                "password": "secret_code",
            }
        }


class UserResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    email: EmailStr = Field(...)
    apikey: str = Field(...)

    class Config:
        allowed_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "_id": "6b78383erfgw8399",
                "name": "John Doe",
                "email": "johndoe@example.com",
                "apikey": "771aa5651339eb44038e2b1ad09f7585b2d53d7adbfa439376645ecfe7d54e6b",
            }
        }


class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        allowed_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "access_token": "6b78383erfgw83996b78383erfgw8399",
                "token_type": "bearer",
            }
        }


class TokenData(BaseModel):
    user_id: Union[str, None] = None


class PasswordReset(BaseModel):
    email: EmailStr


class NewPassword(BaseModel):
    password: str


class Blog(BaseModel):
    title: str = Field(...)
    body: str = Field(...)

    class Config:
        allowed_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "title": "Blog Title",
                "body": "Blog content",
            }
        }


class BlogResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str = Field(...)
    body: str = Field(...)
    author_id: str = Field(...)
    author_name: str = Field(...)
    created_at: str = Field(...)

    class Config:
        allowed_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "_id": "6b78383erfgw8399",
                "title": "Blog Title",
                "body": "Blog content",
                "author_id": "author ID",
                "author_name": "author name",
                "created_at": "date when blog is created",
            }
        }
