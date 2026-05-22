from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class InfluencerStat(db.Model):
    __tablename__ = 'influencer_stats'

    id           = db.Column(db.Integer, primary_key=True)
    platform     = db.Column(db.String(50))
    page_name    = db.Column(db.String(255))
    url          = db.Column(db.String(500))
    followers    = db.Column(db.String(50))
    following    = db.Column(db.String(50))
    category     = db.Column(db.String(255))
    image        = db.Column(db.String(1000))
    subscribers  = db.Column(db.String(50))
    channel_name = db.Column(db.String(255))
    scraped_at   = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<InfluencerStat {self.page_name}>'