import logging

from fastapi import APIRouter, HTTPException

from social_media_fapi.database import comment_table, database, post_table
from social_media_fapi.models.post import (
    Comment,
    CommentIn,
    UserPost,
    UserPostIn,
    UserPostWithComments,
)

router = APIRouter()

logger = logging.getLogger(__name__)


# Going from dict to DB we make function an async function as the DB is async.
async def find_post(post_id: int):
    logger.info(f"Finding post with id {post_id}")
    # The 'c' in 'post_table.c.id' is for column.
    query = post_table.select().where(post_table.c.id == post_id)
    logger.debug(query)
    return await database.fetch_one(query)


@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn) -> UserPost:
    logger.info("Creating post")
    data = post.model_dump()  # Turn the Pydantic model into a dictionary
    # In the .values() the parameter can be a dictionary, and the keys need to match the columns of the DB table.
    query = post_table.insert().values(data)

    logger.debug(query)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/post", response_model=list[UserPost])
async def get_all_posts() -> list[UserPost]:
    logger.info("Get all posts")
    query = post_table.select()
    logger.debug(query)
    return await database.fetch_all(query)


@router.post("/comment", response_model=Comment, status_code=201)
async def create_post(comment: CommentIn) -> UserPost:
    logger.info("Creating comment")
    # Need to add the await here as find post is an async function
    post = await find_post(comment.post_id)
    if not post:
        # Because we have added an exception handler in the main.py (see @app.exception_handler(HTTPException))
        # We no longer need to log the error message here.
        # logger.error(f"Post with id {comment.post_id} not found")
        raise HTTPException(status_code=404, detail="Post not found")

    data = comment.model_dump()  # Turn the Pydantic model into a dictionary
    query = comment_table.insert().values(data)
    logger.debug(query)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/post/{post_id}/comment", response_model=list[Comment])
async def get_comments_on_post(post_id: int):
    logger.info("getting comments on post")
    query = comment_table.select().where(comment_table.c.post_id == post_id)
    logger.debug(query)
    return await database.fetch_all(query)


@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    logger.info("Getting post with comments")
    post = await find_post(post_id)
    if not post:
        # Because we have added an exception handler in the main.py (see @app.exception_handler(HTTPException))
        # We no longer need to log the error message here.
        #logger.error(f"Post with post id {post_id} not found")
        raise HTTPException(status_code=404, detail="Post not found")

    return {"post": post, "comments": await get_comments_on_post(post_id)}
