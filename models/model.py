from sqlalchemy import Column, BigInteger, Integer, String, ForeignKey, TIMESTAMP, Text, Date, func
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# class File(Base):
#     __tablename__ = "files"

#     id = Column(BigInteger, primary_key=True, autoincrement=True)
#     user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
#     file_key = Column(String(500), nullable=False)
#     file_url = Column(String(2048), nullable=False)
#     created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

#     user = relationship("User", back_populates="files")
    
#     def to_dict(self):
#         return {
#             "id": self.id,
#             "file_key": self.file_key,
#             "file_url": self.file_url,
#             "created_at": self.created_at,
#         }
        
class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    reservations = relationship("Reservation", back_populates="user")
    # files = relationship("File", back_populates="user", cascade="all, delete-orphan")

class Concert(Base):
    __tablename__ = "concerts"

    concert_id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    image = Column(String(2048), nullable=True)
    description = Column(Text, nullable=False)
    seat_count = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    place = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    reservations = relationship("Reservation", back_populates="concert")

# Reservation 테이블
class Reservation(Base):
    __tablename__ = "reservations"

    reservation_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    concert_id = Column(BigInteger, ForeignKey("concerts.concert_id", ondelete="CASCADE"), nullable=False)
    reservation_date = Column(TIMESTAMP, server_default=func.current_timestamp())
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    user = relationship("User", back_populates="reservations")
    concert = relationship("Concert", back_populates="reservations")