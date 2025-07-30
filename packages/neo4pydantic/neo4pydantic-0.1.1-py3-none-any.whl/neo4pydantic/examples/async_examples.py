import asyncio
from typing import Optional
from neo4pydantic.async_ import BaseNode, BaseRelationship, AsyncNeo4jClient, IndexManager
from neo4pydantic import Index
import logging

logger = logging.getLogger(__name__)


class Person(BaseNode):
    __label__ = "Person"
    __unique_fields__ = ["email"]
    __indexes__ = [Index(properties=["email"])]

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
    __indexes__ = [Index(properties=["position", "start_date"])]

    position: str
    start_date: Optional[str] = None
    salary: Optional[int] = None


async def main():
    client = AsyncNeo4jClient(
        uri="bolt://localhost:7687", user="neo4j", password="neo4jadmin"
    )
    await client.connect()
    await IndexManager(driver=await client.get_driver()).sync_indexes()

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
        jane = await Person.find_one_by(session, email="janea@example.com")


if __name__ == "__main__":
    asyncio.run(main())
