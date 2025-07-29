import asyncio
from typing import Optional
from neo4pydantic.async_ import BaseNode, BaseRelationship, AsyncClient
import logging

logger = logging.getLogger(__name__)


class Person(BaseNode):
    __label__ = "Person"
    __unique_fields__ = ["email"]
    __indexed_fields__ = ["name", "email"]

    name: str
    email: str
    age: Optional[int] = None
    city: Optional[str] = None


class Company(BaseNode):
    __label__ = "Company"
    __unique_fields__ = ["name"]

    name: str
    industry: Optional[str] = None
    founded_year: Optional[int] = None


class WorksAt(BaseRelationship):
    __type__ = "WORKS_AT"

    position: str
    start_date: Optional[str] = None
    salary: Optional[int] = None


async def main():
    client = AsyncClient(
        uri="bolt://localhost:7687", user="neo4j", password="neo4jadmin"
    )

    async with client.session() as session:
        # Create nodes
        person = Person(
            name="Jane Doe", email="jane@example.com", age=28, city="San Francisco"
        )
        person = await person.save(session)

        company = Company(name="Startup Inc", industry="Technology", founded_year=2020)
        company = await company.save(session)

        # Create relationship
        relationship = WorksAt(
            position="Senior Developer", start_date="2023-03-01", salary=90000
        )
        await relationship.save(session, person, company)

        # Create relationship
        relationship = WorksAt(
            position="Junior Developer", start_date="2022-03-01", salary=90000
        )
        # You can create relationship with custom params option
        await relationship.save_with_custom_params(
            session,
            person.get_label(),
            company.get_label(),
            {"email": person.email},
            {"name": company.name},
        )

        # Query nodes
        people = await Person.find_by(session, city="San Francisco")
        logger.info(f"Person info {people}")
        jane = await Person.find_one_by(session, email="jane@example.com")
        logger.info(f"Jane info {jane}")


if __name__ == "__main__":
    asyncio.run(main())
