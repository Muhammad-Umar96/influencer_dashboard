from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime
from datetime import datetime

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class InfluencerStat(db.Model):
    __tablename__ = 'influencer_stats'

    id:           Mapped[int]           = mapped_column(Integer, primary_key=True)
    platform:     Mapped[str | None]    = mapped_column(String(50))
    page_name:    Mapped[str | None]    = mapped_column(String(255))
    url:          Mapped[str | None]    = mapped_column(String(500))
    followers:    Mapped[str | None]    = mapped_column(String(50))
    following:    Mapped[str | None]    = mapped_column(String(50))
    category:     Mapped[str | None]    = mapped_column(String(255))
    image:        Mapped[str | None]    = mapped_column(String(1000))
    subscribers:  Mapped[str | None]    = mapped_column(String(50))
    channel_name: Mapped[str | None]    = mapped_column(String(255))
    scraped_at:   Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<InfluencerStat {self.page_name}>'