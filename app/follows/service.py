from app.follows.database import FollowDB
from app.follows.schemas import FollowUserOut, FollowStatsOut


class FollowService:
    def __init__(self, db: FollowDB) -> None:
        self.db = db

    def follow(self, follower_id: int, followed_id: int) -> FollowStatsOut:
        # self-follow is blocked at this layer so the DB check constraint is just a safety net
        if follower_id == followed_id:
            raise ValueError("Cannot follow yourself")
        self.db.follow(follower_id, followed_id)
        return FollowStatsOut(**self.db.get_stats(followed_id, viewer_id=follower_id))

    def unfollow(self, follower_id: int, followed_id: int) -> FollowStatsOut:
        if follower_id == followed_id:
            raise ValueError("Cannot unfollow yourself")
        self.db.unfollow(follower_id, followed_id)
        return FollowStatsOut(**self.db.get_stats(followed_id, viewer_id=follower_id))

    def get_followers(self, user_id: int) -> list[FollowUserOut]:
        rows = self.db.get_followers(user_id)
        return [FollowUserOut(**row) for row in rows]

    def get_following(self, user_id: int) -> list[FollowUserOut]:
        rows = self.db.get_following(user_id)
        return [FollowUserOut(**row) for row in rows]

    def get_stats(self, user_id: int, viewer_id: int | None = None) -> FollowStatsOut:
        return FollowStatsOut(**self.db.get_stats(user_id, viewer_id))
