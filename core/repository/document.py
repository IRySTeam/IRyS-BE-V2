from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import text

from app.document.models import Document
from app.user.models import User
from core.db.session import session
from core.repository import BaseRepo


class DocumentRepo(BaseRepo[Document]):
    def __init__(self):
        super().__init__(Document)

    async def get_all(self, include_index: bool = False) -> List[Document]:
        query = select(self.model)
        if include_index:
            query = query.options(selectinload(self.model.index))
        result = await session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, id: int, include_index: bool = False) -> Document:
        query = select(self.model).where(self.model.id == id)
        if include_index:
            query = query.options(selectinload(self.model.index))
        result = await session.execute(query)
        return result.scalars().first()

    async def find_documents_by_repository_id(self, repository_id: int):
        query = (
            select(Document)
            .where(Document.repository_id == repository_id)
            .options(selectinload(Document.index))
        )
        result = await session.execute(query)
        return result.scalars().all()

    async def get_role_by_document_id_and_collaborator_id(
        self, document_id: int, collaborator_id: int
    ) -> Optional[str]:
        query = """
        SELECT ud.role
        FROM user_documents ud
        WHERE ud.user_id = :user_id AND ud.document_id = :document_id
        """
        result = await session.execute(
            text(query), {"user_id": collaborator_id, "document_id": document_id}
        )
        if result.rowcount == 0:
            return None
        return result.fetchone().role

    async def get_collaborators_by_document_id(
        self, document_id: int, repository_id: int
    ) -> List[User]:
        sql = """
        SELECT u.*, 'Owner' AS role
        FROM users u
        INNER JOIN user_repositories ur ON ur.user_id = u.id
        WHERE ur.repository_id = :repository_id AND ur.role IN ('Owner', 'Admin')
        UNION
        SELECT u.*, ud.role
        FROM users u
        JOIN user_documents ud ON ud.user_id = u.id
        WHERE ud.document_id = :document_id
        """
        result = await session.execute(
            text(sql), {"document_id": document_id, "repository_id": repository_id}
        )
        return result.fetchall()

    async def add_collaborator(self, document_id: int, collaborator_id: int, role: str):
        query = """
        INSERT INTO user_documents (user_id, document_id, role)
        VALUES (:user_id, :document_id, :role)
        """
        await session.execute(
            text(query),
            {"user_id": collaborator_id, "document_id": document_id, "role": role},
        )
        await session.commit()

    async def edit_collaborator(
        self, document_id: int, collaborator_id: int, role: str
    ):
        query = """
        UPDATE user_documents
        SET role = :role
        WHERE user_id = :user_id AND document_id = :document_id
        """
        await session.execute(
            text(query),
            {"user_id": collaborator_id, "document_id": document_id, "role": role},
        )
        await session.commit()

    async def delete_collaborator(self, document_id: int, collaborator_id: int):
        query = """
        DELETE FROM user_documents
        WHERE user_id = :user_id AND document_id = :document_id
        """
        await session.execute(
            text(query),
            {"user_id": collaborator_id, "document_id": document_id},
        )
        await session.commit()

    async def is_collaborator_exist(
        self, document_id: int, collaborator_id: int
    ) -> bool:
        query = """
        SELECT COUNT(*) AS count
        FROM user_documents
        WHERE user_id = :user_id AND document_id = :document_id
        """
        result = await session.execute(
            text(query),
            {"user_id": collaborator_id, "document_id": document_id},
        )
        return result.fetchone().count > 0
