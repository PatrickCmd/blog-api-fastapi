from datetime import datetime
from typing import List

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder

from ..schemas import Blog, BlogResponse, User, db
from ..utils.auth2 import get_current_user

router = APIRouter(
    prefix="/blog",
    tags=["Blog"],
)


@router.post(
    "",
    response_description="Create a blog post",
    response_model=BlogResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_blog(blog_info: Blog, current_user: User = Depends(get_current_user)):
    try:
        blog_info = jsonable_encoder(blog_info)
        blog_info["author_id"] = current_user["_id"]
        blog_info["author_name"] = current_user["name"]
        blog_info["created_at"] = str(datetime.utcnow())
        # create new bog
        new_blog = await db["blog_posts"].insert_one(blog_info)
        created_blog_post = await db["blog_posts"].find_one(
            {"_id": new_blog.inserted_id}
        )

        return created_blog_post
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid data entered.",
        )


@router.get(
    "/posts", response_description="Get blog posts", response_model=List[BlogResponse]
)
async def get_blog_posts(limit: int = 4, orderby: str = "created_at"):
    try:
        blog_posts = (
            await db["blog_posts"]
            .find({"$query": {}, "$orderby": {orderby: -1}})
            .to_list(limit)
        )
        return blog_posts
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error.",
        )


@router.get("/{id}", response_description="Get blog post", response_model=BlogResponse)
async def get_blog_post(id: str):
    try:
        blog_post = await db["blog_posts"].find_one({"_id": ObjectId(id)})

        if blog_post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blog post with ID {id} is not found.",
            )
        return blog_post
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error (Make sure valid post ID is used).",
        )


@router.put(
    "/{id}", response_description="Update blog post", response_model=BlogResponse
)
async def update_blog_post(
    id: str, blog_info: Blog, current_user: User = Depends(get_current_user)
):
    try:
        id = ObjectId(id)
        blog_post = await db["blog_posts"].find_one({"_id": id})

        if blog_post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blog post with ID {id} is not found.",
            )

        if blog_post["author_id"] == current_user["_id"]:
            blog_info = {k: v for k, v in blog_info.dict().items() if v is not None}
            if len(blog_info) >= 1:
                blog_post_update = await db["blog_posts"].update_one(
                    {"_id": id}, {"$set": blog_info}
                )
                if blog_post_update.modified_count == 1:
                    updated_blog = await db["blog_posts"].find_one({"_id": id})
                    return updated_blog
                else:
                    blog = await db["blog_posts"].find_one({"_id": id})
                    return blog
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You have no permissions to perform this action.",
            )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error (Make sure valid post ID is used).",
        )


@router.delete(
    "/{id}",
    response_description="Delete blog post",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_blog_post(id: str, current_user: User = Depends(get_current_user)):
    try:
        id = ObjectId(id)
        blog_post = await db["blog_posts"].find_one({"_id": id})

        if blog_post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blog post with ID {id} is not found.",
            )

        if blog_post["author_id"] == current_user["_id"]:
            await db["blog_posts"].delete_one({"_id": id})
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You have no permissions to perform this action.",
            )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error (Make sure valid post ID is used).",
        )
