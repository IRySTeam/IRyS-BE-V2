from typing import Tuple, List, Optional
from sqlalchemy import select, and_
from sqlalchemy.sql import text

from core.repository import BaseRepo
from app.repository.models import Repository
from core.db.session import session
from app.user.models import user_repositories, User


class RepositoryRepo(BaseRepo[Repository]):
    def __init__(self):
        super().__init__(Repository)

    async def save(self, user_id: int, params: dict, role: str) -> None:
        new_repo = Repository(**params)
        session.add(new_repo)
        await session.flush()

        # Add the new Repository to the User's repositories with the role using session.execute()
        stmt = user_repositories.insert().values(
            user_id=user_id, repository_id=new_repo.id, role=role
        )
        await session.execute(stmt)

    async def get_joined_repositories(
        self,
        user_id: int,
        name: str,
        type: str,
        order_by: str,
        page_no: int,
        page_size: int,
    ) -> Tuple[List, int, int]:
        query = """
        SELECT DISTINCT r.*, a2.owner_id, a2.owner_first_name, a2.owner_last_name
        FROM repositories r
        INNER JOIN user_repositories ur ON ur.repository_id = r.id
        INNER JOIN
        (
            SELECT u2.id AS owner_id, u2.first_name AS owner_first_name, u2.last_name AS owner_last_name, r2.id AS repository_id
            FROM users u2
            INNER JOIN user_repositories ur2 ON u2.id = ur2.user_id
            INNER JOIN repositories r2 ON ur2.repository_id = r2.id
            WHERE ur2.role = 'Owner'
        ) a2 ON ur.repository_id = a2.repository_id
        WHERE ur.user_id = :user_id
        """

        # Add search filter if provided
        if name:
            query += " AND r.name ILIKE :search"

        # Add is_public filter if provided
        if type:
            if type == "public":
                query += " AND r.is_public = TRUE"
            elif type == "private":
                query += " AND r.is_public = FALSE"

        # Add order by clause based on user input
        if order_by:
            if order_by == "updated_at":
                order_by = "r.updated_at DESC"
            elif order_by == "name":
                order_by = "r.name ASC"
            query += f" ORDER BY {order_by}"

        # Add limit and offset
        query += " LIMIT :limit OFFSET :offset"
        limit = page_size
        offset = (page_no - 1) * page_size

        # Execute the raw SQL query with parameters
        results = await session.execute(
            text(query),
            {
                "user_id": user_id,
                "search": f"%{name}%",
                "limit": limit,
                "offset": offset,
            },
        )

        # Fetch the results
        repositories = results.fetchall()

        count_query = """
            SELECT COUNT(r.id) as total_count
            FROM repositories r
            INNER JOIN user_repositories ur ON ur.repository_id = r.id
            WHERE ur.user_id = :user_id
        """
        # Add search filter if provided
        if name:
            count_query += " AND r.name ILIKE :search"

        if type:
            if type == "public":
                count_query += " AND r.is_public = TRUE"
            elif type == "private":
                count_query += " AND r.is_public = FALSE"

        count_result = await session.execute(
            text(count_query), {"user_id": user_id, "search": f"%{name}%"}
        )
        total_items = count_result.fetchone().total_count
        total_pages = (total_items + limit - 1) // limit

        return repositories, total_pages, total_items

    async def get_public_repositories(
        self, name: str, page_no: int, page_size: int
    ) -> Tuple[List, int, int]:
        query = """
            SELECT DISTINCT r.*, a2.owner_id, a2.owner_first_name, a2.owner_last_name
            FROM repositories r
            INNER JOIN user_repositories ur ON ur.repository_id = r.id
            INNER JOIN
            (
                SELECT u2.id AS owner_id, u2.first_name AS owner_first_name, u2.last_name AS owner_last_name, r2.id AS repository_id
                FROM users u2
                INNER JOIN user_repositories ur2 ON u2.id = ur2.user_id
                INNER JOIN repositories r2 ON ur2.repository_id = r2.id
                WHERE ur2.role = 'Owner'
            ) a2 ON ur.repository_id = a2.repository_id
            WHERE r.is_public = TRUE
        """

        # Add search filter if provided
        if name:
            query += " AND r.name ILIKE :search"

        # Add limit and offset
        query += " LIMIT :limit OFFSET :offset"
        limit = page_size
        offset = (page_no - 1) * page_size

        # Execute the raw SQL query with parameters
        results = await session.execute(
            text(query),
            {
                "search": f"%{name}%",
                "limit": limit,
                "offset": offset,
            },
        )

        # Fetch the results
        repositories = results.fetchall()

        count_query = """
            SELECT COUNT(r.id) as total_count
            FROM repositories r
            WHERE r.is_public = TRUE
        """
        # Add search filter if provided
        if name:
            count_query += " AND r.name ILIKE :search"

        count_result = await session.execute(text(count_query), {"search": f"%{name}%"})
        total_items = count_result.fetchone().total_count
        total_pages = (total_items + limit - 1) // limit

        return repositories, total_pages, total_items

    async def get_repository_collaborators(self, repository_id: int) -> List[User]:
        query = """
        SELECT u.*, ur.role
        FROM users u
        INNER JOIN user_repositories ur ON ur.user_id = u.id
        WHERE ur.repository_id = :repository_id
        """
        results = await session.execute(text(query), {"repository_id": repository_id})
        return results.fetchall()

    async def get_collaborator_by_id(self, user_id: int, repository_id: int):
        sql = text(
            """
            SELECT u.*, ur.role
            FROM users u
            INNER JOIN user_repositories ur ON ur.user_id = u.id
            WHERE ur.repository_id = :repository_id
            AND u.id = :user_id
        """
        )
        params = {"repository_id": repository_id, "user_id": user_id}

        # Execute SQL query and fetch result
        result = await session.execute(sql, params)
        return result.fetchone()

    async def is_user_id_collaborator_of_repository(
        self, user_id: int, repository_id: int
    ) -> bool:
        query = """
        SELECT COUNT(*) as total_count
        FROM user_repositories ur
        WHERE ur.user_id = :user_id AND ur.repository_id = :repository_id
        """
        results = await session.execute(
            text(query), {"user_id": user_id, "repository_id": repository_id}
        )
        return results.fetchone().total_count > 0

    async def is_user_id_owner_of_repository(self, user_id: int, repository_id: int):
        sql = text(
            """
            SELECT 1
            FROM user_repositories ur
            WHERE ur.user_id = :user_id
            AND ur.repository_id = :repository_id
            AND ur.role = 'Owner'
        """
        )
        params = {"user_id": user_id, "repository_id": repository_id}

        # Execute SQL query and fetch result
        result = await session.execute(sql, params)
        row = result.fetchone()

        # Check if user is owner of the repository
        is_owner = True if row else False

        return is_owner

    async def is_user_id_admin_of_repository(self, user_id: int, repository_id: int):
        sql = text(
            """
            SELECT 1
            FROM user_repositories ur
            WHERE ur.user_id = :user_id
            AND ur.repository_id = :repository_id
            AND ur.role = 'Admin'
        """
        )
        params = {"user_id": user_id, "repository_id": repository_id}

        # Execute SQL query and fetch result
        result = await session.execute(sql, params)
        row = result.fetchone()

        # Check if user is owner of the repository
        is_owner = True if row else False

        return is_owner

    async def get_repository_by_id(self, repository_id: int) -> Repository:
        query = """
            SELECT r.*, a2.owner_id, a2.owner_first_name, a2.owner_last_name
            FROM repositories r
            INNER JOIN
            (
                SELECT u2.id AS owner_id, u2.first_name AS owner_first_name, u2.last_name AS owner_last_name, r2.id AS repository_id
                FROM users u2
                INNER JOIN user_repositories ur2 ON u2.id = ur2.user_id
                INNER JOIN repositories r2 ON ur2.repository_id = r2.id
                WHERE ur2.role = 'Owner'
            ) a2 ON r.id = a2.repository_id
            WHERE r.id = :repository_id
        """
        result = await session.execute(text(query), {"repository_id": repository_id})
        repository = result.fetchone()
        return repository

    async def create_user_repository(
        self, user_id: int, repository_id: int, role: str
    ) -> None:
        sql = text(
            """
            INSERT INTO user_repositories (user_id, repository_id, role)
            VALUES (:user_id, :repository_id, :role)
        """
        )
        params = {
            "user_id": user_id,
            "repository_id": repository_id,
            "role": role,
        }

        # Execute SQL query
        await session.execute(sql, params)

    async def delete_user_repository(self, user_id: int, repository_id: int) -> None:
        sql = text(
            """
            DELETE FROM user_repositories
            WHERE user_id = :user_id AND repository_id = :repository_id
        """
        )
        params = {
            "user_id": user_id,
            "repository_id": repository_id,
        }

        # Execute SQL query
        await session.execute(sql, params)

    async def update_user_repository_role(
        self, user_id: int, repository_id: int, role: str
    ) -> None:
        sql = text(
            """
            UPDATE user_repositories
            SET role = :role
            WHERE user_id = :user_id AND repository_id = :repository_id
        """
        )
        params = {
            "user_id": user_id,
            "repository_id": repository_id,
            "role": role,
        }

        # Execute SQL query
        await session.execute(sql, params)

    async def does_user_id_have_any_repository(self, user_id: int) -> bool:
        query = """
        SELECT ur.role
        FROM user_repositories ur
        WHERE ur.user_id = :user_id AND ur.repository_id = :repository_id
        """
        result = await session.execute(text(query), {"user_id": user_id})
        total_items = result.fetchone().total_count
        return total_items > 0

    async def get_user_role_by_user_id_and_repository_id(
        self, user_id: int, repository_id: int
    ) -> Optional[str]:
        query = """
        SELECT ur.role
        FROM user_repositories ur
        WHERE ur.user_id = :user_id AND ur.repository_id = :repository_id
        """
        result = await session.execute(
            text(query), {"user_id": user_id, "repository_id": repository_id}
        )
        if result.rowcount == 0:
            return None
        return result.fetchone().role
