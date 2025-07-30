"""Custom exceptions"""

class Neo4PydanticException(Exception):
    """Base exception for all neo4pydantic error"""
    pass

class QueryError(Neo4PydanticException):
    def __init__(self, message: str, query: str = None, params: dict = None):
        super().__init__(message)
        self.query = query
        self.params = params

    def __str__(self):
        base = super().__str__()
        return f"{base}\nQuery: {self.query}\nParams: {self.params}"

class CreateIndexError(Neo4PydanticException):
    def __init__(self, message: str, index_name: str, query: str = None):
        super().__init__(message)
        self.query = query
        self.index_name = index_name

    def __str__(self):
        base = super().__str__()
        return f"{base}\n Error when create index {self.index_name}\nQuery: {self.query}"
