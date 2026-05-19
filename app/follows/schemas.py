from pydantic import BaseModel


class FollowUserOut(BaseModel):
    id: int
    name: str
    avatar_id: str | None = None


class FollowStatsOut(BaseModel):
    followers_count: int
    following_count: int
    is_following: bool
