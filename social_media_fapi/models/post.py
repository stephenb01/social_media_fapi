from pydantic import BaseModel


class UserPostIn(BaseModel):
    body: str


class UserPost(UserPostIn):
    id: int


class CommentIn(BaseModel):
    body: str
    post_id: int


class Comment(CommentIn):
    id: int


class UserPostWithComments(BaseModel):
    post: UserPost
    comments: list[Comment]


"""
The class UserPostWithComments gives us the following data structure
{
 "post": { "id": 0, "body": "My Post"}
 "comment": [{ "id": 2, "post_id": 0, "body": "My comment"}]
}
"""
