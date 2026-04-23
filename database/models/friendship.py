from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from database.db import Base


class Friendship(Base):
    __tablename__ = "friendships"

    id = Column(Integer, primary_key=True)

    requester_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    addressee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    status = Column(String(10))  # pending / accepted / blocked