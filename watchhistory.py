from app import db

class WatchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, nullable=False)
    watched_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<WatchHistory user_id={self.user_id} video_id={self.video_id} watched_at={self.watched_at}>"

def add_watch_history(user_id: int, video_id: int, watched_at):
    history = WatchHistory(user_id=user_id, video_id=video_id, watched_at=watched_at)
    db.session.add(history)
    db.session.commit()
    return history

def get_watch_history(user_id: int):
    return WatchHistory.query.filter_by(user_id=user_id).order_by(WatchHistory.watched_at.desc()).all()

def export_watch_history(user_id: int):
    """
    Returns a list of watch history records for the given user_id,
    each as a dictionary.
    """
    history = get_watch_history(user_id)
    return [
        {
            'id': h.id,
            'user_id': h.user_id,
            'video_id': h.video_id,
            'watched_at': h.watched_at.isoformat() if h.watched_at else None
        }
        for h in history
    ]