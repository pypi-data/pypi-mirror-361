from typing import Optional
from neo4pydantic.sync import BaseNode, BaseRelationship, SyncClient
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


# Usage example
def main():
    client = SyncClient(
        uri="bolt://localhost:7687", user="neo4j", password="neo4jadmin"
    )

    with client.session() as session:
        # Create nodes
        person = Person(
            name="John Doe", email="john@example.com", age=30, city="New York"
        )
        person = person.save(session)

        company = Company(name="Tech Corp", industry="Technology", founded_year=2010)
        company = company.save(session)

        # Create relationship
        relationship = WorksAt(
            position="Software Engineer", start_date="2023-01-15", salary=75000
        )
        relationship.save(session, person, company)

        # Create relationship
        relationship = WorksAt(
            position="Junior Developer", start_date="2022-03-01", salary=90000
        )
        # You can create relationship with custom params option
        relationship.save_with_custom_params(
            session,
            person.get_label(),
            company.get_label(),
            {"email": person.email},
            {"name": company.name},
        )

        # Query nodes
        people = Person.find_by(session, city="New York")
        logger.info(f"Person info {people}")
        john = Person.find_one_by(session, email="john@example.com")
        logger.info(f"John info {john}")


if __name__ == "__main__":
    main()
