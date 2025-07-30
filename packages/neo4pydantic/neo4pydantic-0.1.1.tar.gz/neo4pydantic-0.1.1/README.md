# neo4pydantic

A Pydantic-based Neo4j ORM with async/sync support.

[![PyPI Release](https://img.shields.io/pypi/v/neo4pydantic)](https://pypi.org/project/neo4pydantic/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repo-blue?logo=github)](https://github.com/Rheagal98/neo4pydantic)

## Overview

**neo4pydantic** provides an easy way to define Neo4j nodes and relationships as Pydantic models, and interact with a Neo4j database using both synchronous and asynchronous clients. It supports automatic type conversion, unique and indexed fields, and convenient CRUD operations.

## Features

- Define Neo4j nodes and relationships as Pydantic models
- Sync and async client support
- Automatic type conversion for Neo4j temporal types
- Unique and indexed field support for efficient queries
- Simple CRUD operations for nodes and relationships

## Installation

```bash
pip install neo4pydantic
```

## Quick Start

### 1. Define Your Models

```python
from neo4pydantic import BaseNode, BaseRelationship

class Person(BaseNode):
    __label__ = "Person"
    __unique_fields__ = ["email"]

    name: str
    email: str
    age: int | None = None
    city: str | None = None

class Company(BaseNode):
    __label__ = "Company"
    __unique_fields__ = ["name"]

    name: str
    industry: str | None = None
    founded_year: int | None = None

class WorksAt(BaseRelationship):
    __type__ = "WORKS_AT"
    position: str
    start_date: str | None = None
    salary: int | None = None
```

### 2. Synchronous Usage

```python
from neo4pydantic import Neo4jClient

client = Neo4jClient(uri="bolt://localhost:7687", user="neo4j", password="your_password")
with client.session() as session:
  person = Person(name="John Doe", email="john@example.com", age=30, city="New York").save(session)
  company = Company(name="Tech Corp", industry="Technology", founded_year=2010).save(session)
  relationship = WorksAt(position="Software Engineer", start_date="2023-01-15", salary=75000)
  relationship.save(session, person, company)
  # Query
  people = Person.find_by(session, city="New York")
```

### 3. Asynchronous Usage
Note that all asynchronous usage is the same as synchronous function
```python
import asyncio
from neo4pydantic.async_ import AsyncNeo4jClient, BaseNode, BaseRelationship


async def main():
  client = AsyncNeo4jClient(uri="bolt://localhost:7687", user="neo4j", password="your_password")
  async with client.session() as session:
    person = Person(name="Jane Doe", email="jane@example.com", age=28, city="San Francisco")
    person = await person.save(session)
    company = Company(name="Startup Inc", industry="Technology", founded_year=2020)
    company = await company.save(session)
    relationship = WorksAt(position="Senior Developer", start_date="2023-03-01", salary=90000)
    await relationship.save(session, person, company)
    # Query
    people = await Person.find_by(session, city="San Francisco")


asyncio.run(main())
```

## Querying and Advanced Usage

### Find Multiple Nodes (`find_by`)

```python
# Find all people in New York
people = Person.find_by(session, city="New York")
for person in people:
    print(person)
```

### Find a Single Node (`find_one_by`)

```python
# Find a person by email
john = Person.find_one_by(session, email="john@example.com")
print(john)
```

### Delete A Node (`find_one_by`)

```python
# Delete a person
john = Person(id=10, mail="john@example.com").delete(session)
```

### Automatically create indexes when startup

```python
from neo4pydantic import IndexManager, Neo4jClient

client = Neo4jClient(uri="bolt://localhost:7687", user="neo4j", password="your_password")

def init_indexes():
    # Import your custom model here so that the IndexManger can acknowledge your model before create the indexes
    from your_custom_model import Person, Company, WorkFor
    
    client.connect()
    created_indexes = IndexManager(client.get_driver()).sync_indexes()
    print(created_indexes)
```

---

### Create Relationship with Custom Parameters (`save_with_custom_params`)

```python
relationship = WorksAt(position="Junior Developer", start_date="2022-03-01", salary=90000)
relationship.save_with_custom_params(
    session,
    from_node_label=person.get_label(),
    to_node_label=company.get_label(),
    from_node_params={"email": person.email},
    to_node_params={"name": company.name},
)
```

---

## Directory Structure

- `neo4pydantic/`
  - `sync/` - Synchronous client and base classes
  - `async_/` - Asynchronous client and base classes
  - `core/` - Core logic and base models
  - `utils/` - Type conversion utilities
  - `examples/` - Example scripts for sync and async usage
- `tests/` - Unit tests

## Requirements

- Python 3.8+
- Neo4j 5.x
- Pydantic 2.x

## License

MIT License © 2025 Edward Chu
