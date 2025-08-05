from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from config import DB_URL

engine = create_async_engine(DB_URL, echo=False)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Textbook(Base):
    __tablename__ = "textbooks"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    chapters: Mapped[list["Chapter"]] = relationship(back_populates="textbook")
    status: Mapped[str] = mapped_column(String, default="awaiting")


class Chapter(Base):
    __tablename__ = "chapters"
    __table_args__ = (
        UniqueConstraint("name", "textbook_id", name="uq_chapter_name_per_textbook"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    textbook_id: Mapped[int] = mapped_column(ForeignKey("textbooks.id"), nullable=False)
    textbook: Mapped["Textbook"] = relationship(back_populates="chapters")
    problems: Mapped[list["Problem"]] = relationship(back_populates="chapter")
    status: Mapped[str] = mapped_column(String, default="awaiting")


class Problem(Base):
    __tablename__ = "problems"
    __table_args__ = (
        UniqueConstraint("name", "chapter_id", name="uq_problem_name_per_chapter"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapters.id"), nullable=False)
    chapter: Mapped["Chapter"] = relationship(back_populates="problems")
    solutions: Mapped[list["Solution"]] = relationship(back_populates="problem")
    status: Mapped[str] = mapped_column(String, default="awaiting")


class Solution(Base):
    __tablename__ = "solutions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(String)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_file_ids: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"))
    problem: Mapped["Problem"] = relationship(back_populates="solutions")
    status: Mapped[str] = mapped_column(String, default="awaiting")

