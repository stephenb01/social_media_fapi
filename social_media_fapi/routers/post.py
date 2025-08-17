import logging
from typing import Annotated
import sqlalchemy
from enum import Enum
from fastapi import APIRouter, Depends, HTTPException

from social_media_fapi.database import comment_table, database, like_table, post_table
from social_media_fapi.models.post import (
    Comment,
    CommentIn,
    PostLike,
    PostLikeIn,
    UserPost,
    UserPostIn,
    UserPostWithComments,
    UserPostWithLikes,
)
from social_media_fapi.models.user import User
from social_media_fapi.security import get_current_user

router = APIRouter()

logger = logging.getLogger(__name__)

select_post_and_likes = (
    sqlalchemy.select(post_table, sqlalchemy.func.count(like_table.c.id).label("likes"))
    .select_from(post_table.outerjoin(like_table))
    .group_by(post_table.c.id)
)


# Going from dict to DB we make function an async function as the DB is async.
async def find_post(post_id: int):
    logger.info(f"Finding post with id {post_id}")
    # The 'c' in 'post_table.c.id' is for column.
    query = post_table.select().where(post_table.c.id == post_id)
    logger.debug(query)
    return await database.fetch_one(query)


@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(
    post: UserPostIn, current_user: Annotated[User, Depends(get_current_user)]
) -> UserPost:
    logger.info("Creating post")

    # This post.model_dump() Turns the Pydantic model into a dictionary
    data = {**post.model_dump(), "user_id": current_user.id}
    # In the .values() the parameter can be a dictionary, and the keys need to match the columns of the DB table.
    query = post_table.insert().values(data)

    logger.debug(query)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


class PostSorting(str, Enum):
    new = "new"
    old = "old"
    most_likes = "most_likes"


@router.get("/post", response_model=list[UserPostWithLikes])
async def get_all_posts(
    sorting: PostSorting = PostSorting.new,
) -> list[UserPostWithLikes]:  # http://api.com/post?sorting=most_likes
    logger.info("Get all posts")

    """
    query = select_post_and_likes.order_by(sqlalchemy.desc(post_table.c.id))
    query = select_post_and_likes.order_by(post_table.c.id.desc())
        Out of the two lins above, the second one is the preferred one.
        As we are unsing the sqlalchemy ORM, we can use the following one ONLY if you don't have a clumn object:
        select_post_and_likes.order_by(sqlalchemy.desc("likes"))
    """

    match sorting:
        case PostSorting.new:
            query = select_post_and_likes.order_by(post_table.c.id.desc())
        case PostSorting.old:
            query = select_post_and_likes.order_by(post_table.c.id.asc())
        case PostSorting.most_likes:
            query = select_post_and_likes.order_by(sqlalchemy.desc("likes"))

    # The above match statement is equivalent to the following if-elif-else block:
    # if sorting == PostSorting.new:
    #     query = select_post_and_likes.order_by(post_table.c.id.desc())
    # elif sorting == PostSorting.old:
    #     query = select_post_and_likes.order_by(post_table.c.id.asc())
    # elif sorting == PostSorting.most_likes:
    #     query = select_post_and_likes.order_by(sqlalchemy.desc("likes"))

    logger.debug(query)

    return await database.fetch_all(query)


@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(
    comment: CommentIn, current_user: Annotated[User, Depends(get_current_user)]
) -> UserPost:
    logger.info("Creating comment")

    # Need to add the await here as find post is an async function
    post = await find_post(comment.post_id)
    if not post:
        # Because we have added an exception handler in the main.py (see @app.exception_handler(HTTPException))
        # We no longer need to log the error message here.
        # logger.error(f"Post with id {comment.post_id} not found")
        raise HTTPException(status_code=404, detail="Post not found")

    # comment.model_dump() - Turn the Pydantic model into a dictionary
    data = {**comment.model_dump(), "user_id": current_user.id}
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

    query = select_post_and_likes.where(post_table.c.id == post_id)
    logger.debug(query)
    post = await database.fetch_one(query)

    if not post:
        # Because we have added an exception handler in the main.py (see @app.exception_handler(HTTPException))
        # We no longer need to log the error message here.
        # logger.error(f"Post with post id {post_id} not found")
        raise HTTPException(status_code=404, detail="Post not found")

    return {"post": post, "comments": await get_comments_on_post(post_id)}


@router.post("/like", response_model=PostLike, status_code=201)
async def like_post(
    post_like: PostLikeIn, current_user: Annotated[User, Depends(get_current_user)]
) -> PostLike:
    logger.info("Liking post")

    # Need to add the await here as find post is an async function
    post = await find_post(post_like.post_id)
    if not post:
        # Because we have added an exception handler in the main.py (see @app.exception_handler(HTTPException))
        # We no longer need to log the error message here.
        # logger.error(f"Post with id {post_like.post_id} not found")
        raise HTTPException(status_code=404, detail="Post not found")

    data = {**post_like.model_dump(), "user_id": current_user.id}
    query = like_table.insert().values(data)
    logger.debug(query)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}
