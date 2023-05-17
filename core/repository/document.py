from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import text

from app.document.models import Document
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

    async def get_repository_documents_count(
        self,
        repository_id: int,
    ) -> int:
        query = select(self.model).where(self.model.repository_id == repository_id)
        result = await session.execute(query)
        return len(result.scalars().all())

    async def get_by_id(self, id: int, include_index: bool = False) -> Document:
        query = select(self.model).where(self.model.id == id)
        if include_index:
            query = query.options(selectinload(self.model.index))
        result = await session.execute(query)
        return result.scalars().first()

    async def get_by_ids(
        self, ids: List[int], include_index: bool = False
    ) -> List[Document]:
        query = select(self.model).where(self.model.id.in_(ids))
        if include_index:
            query = query.options(selectinload(self.model.index))
        result = await session.execute(query)
        return result.scalars().all()

    async def find_documents_by_repository_id(self, repository_id: int):
        query = (
            select(Document)
            .where(Document.repository_id == repository_id)
            .options(selectinload(Document.index))
        )
        result = await session.execute(query)
        return result.scalars().all()

    async def get_all_documents_in_repo(
        self,
        repository_id: int,
        status: str = "ALL",
        page_size: int = 10,
        page_no: int = 1,
        find_document: str = None,
        include_index: bool = True,
    ) -> dict:
        query = select(Document).where(Document.repository_id == repository_id)

        if include_index:
            query = query.options(selectinload(Document.index))

        if status != "ALL":
            query = query.where(Document.index.has(status=status))

        if find_document:
            query = query.where(Document.title.ilike(f"%{find_document}%"))

        result = await session.execute(query)
        full_items = result.fetchall()
        total_items = len(full_items)
        total_pages = (total_items + page_size - 1) // page_size

        query = query.limit(page_size).offset((page_no - 1) * page_size)
        result = await session.execute(query)
        data = result.scalars().all()

        return {
            "results": data,
            "current_page": page_no,
            "total_pages": total_pages,
            "total_items": total_items,
        }

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
    ) -> list:
        sql = """
        SELECT * FROM
        (SELECT u.*, 'Owner' AS role
        FROM users u
        INNER JOIN user_repositories ur ON ur.user_id = u.id
        WHERE ur.repository_id = :repository_id AND ur.role IN ('Owner', 'Admin')
        UNION
        SELECT u.*, ud.role
        FROM users u
        JOIN user_documents ud ON ud.user_id = u.id
        WHERE ud.document_id = :document_id) AS data
        ORDER BY array_position(array['Owner', 'Editor', 'Viewer'], data.role)
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

    async def get_all_accessible_documents(self, collaborator_id: int) -> List[int]:
        query = """
        SELECT d.id FROM documents d
        INNER JOIN user_documents ud ON d.id = ud.document_id
        WHERE user_id = :user_id
        UNION
        SELECT d.id FROM documents d
        INNER JOIN repositories r ON d.repository_id = r.id
        INNER JOIN user_repositories ur ON r.id = ur.repository_id
        WHERE ur.user_id = :user_id
        UNION
        SELECT d.id FROM documents d
        WHERE d.is_public IS true;
        """
        result = await session.execute(text(query), {"user_id": collaborator_id})
        return [r.id for r in result.fetchall()]

    async def get_repo_accessible_documents(self, repository_id: int) -> List[int]:
        query = """
        SELECT d.id FROM documents d
        INNER JOIN repositories r ON d.repository_id = r.id
        INNER JOIN user_repositories ur ON r.id = ur.repository_id
        WHERE r.id = :repository_id;
        """
        result = await session.execute(text(query), {"repository_id": repository_id})
        return [r.id for r in result.fetchall()]

    async def delete_by_repository_id(self, repository_id: int):
        sql = """
        DELETE FROM documents
        WHERE repository_id = :repository_id
        """
        await session.execute(text(sql), {"repository_id": repository_id})

    async def delete_user_documents_by_document_id(self, document_id: int):
        sql = """
        DELETE FROM user_documents
        WHERE document_id = :document_id
        """
        await session.execute(text(sql), {"document_id": document_id})

    async def delete_user_documents_by_repository_id(self, repository_id: int):
        sql = """
        DELETE FROM user_documents
        WHERE document_id IN (
            SELECT d.id
            FROM documents d
            WHERE d.repository_id = :repository_id
        )
        """
        await session.execute(text(sql), {"repository_id": repository_id})

    async def delete_user_documents_viewer_by_document_id(self, document_id: int):
        sql = """
        DELETE FROM user_documents
        WHERE document_id = :document_id AND role = 'Viewer'
        """
        await session.execute(text(sql), {"document_id": document_id})

    async def delete_by_id(self, id: int):
        sql = """
        DELETE FROM documents
        WHERE id = :id
        """
        await session.execute(text(sql), {"id": id})
