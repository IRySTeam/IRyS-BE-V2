from typing import TypeVar, Type, Optional, Generic

from sqlalchemy import select, update, delete, insert

from core.db.session import Base, session
from core.repository.enum import SynchronizeSessionEnum

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepo(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        result = await session.execute(query)
        return result.scalars().first()

    async def update_by_id(
        self,
        id: int,
        params: dict,
        synchronize_session: SynchronizeSessionEnum = False,
    ):
        query = (
            update(self.model)
            .where(self.model.id == id)
            .values(**params)
            .execution_options(synchronize_session=synchronize_session)
        )
        await session.execute(query)

    async def delete(self, model: ModelType) -> None:
        await session.delete(model)

    async def delete_by_id(
        self,
        id: int,
        synchronize_session: SynchronizeSessionEnum = False,
    ) -> None:
        query = (
            delete(self.model)
            .where(self.model.id == id)
            .execution_options(synchronize_session=synchronize_session)
        )
        await session.execute(query)
        await session.commit()

    async def save(self, params: dict) -> ModelType:
        query = insert(self.model).values(**params)
        return await session.execute(query)

    async def is_exist(self, id: int) -> bool:
        row = await session.get(self.model, id)
        if row:
            return True
        else:
            return False
