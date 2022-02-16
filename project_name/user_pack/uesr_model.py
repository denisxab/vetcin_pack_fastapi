from asyncio import run
from typing import Optional

from sqlalchemy import Boolean, Column, Integer, String, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database import Base, engine, hashRandom


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    token = Column(String, unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    @staticmethod
    async def register_new_user(session: AsyncSession, **kwargs):
        """
        :param session:
        :param kwargs:
        """
        sql_ = User(**kwargs)
        session.add(sql_)
        await session.flush()
        # Получить id пользователя
        await session.refresh(sql_)
        await session.commit()
        return sql_.id

    @staticmethod
    async def login_user(session: AsyncSession, email: str, hashed_password: str) -> Optional[object]:
        obj_ = await session.execute(select(User.id).where((User.email == email) &
                                                           (User.hashed_password == hashed_password)))
        res = obj_.first()
        if res:
            return res[0]

    @staticmethod
    async def create_token(session: AsyncSession, id_: int) -> Optional[str]:
        hash_ = hashRandom()
        res = await session.execute(update(User).where(User.id == id_).values(token=hash_))
        # Если получилось обновить данные, вернем хеш
        if res.rowcount > 1:
            return hash_
        return None

    @staticmethod
    async def get_token(session: AsyncSession, id_: int) -> str:
        obj_ = await session.execute(select(User.token).where(User.id == id_))
        res = obj_.first()
        if res:
            return res[0]

    def __repr__(self):
        return f"{self.id}:{self.email}"


regex_email: str = "([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"


async def init_models():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


if __name__ == '__main__':
    run(init_models())
