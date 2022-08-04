def chaineable(f):
    def wrapper(*args):
        f(*args)
        return args[0]
    return wrapper


class QueryBuilder:
    def __init__(self) -> None:
        self._query = {}
        self._root_key = '$and'

    def __repr__(self) -> str:
        return str(self.query)

    def __str__(self) -> str:
        return str(self.query)

    @property
    def query(self) -> dict:
        return self._query

    def _init_query(self) -> None:
        self._query = {self._root_key: []}

    def _is_query_empty(self)-> None:
        return self._root_key not in self._query

    def _add_to_query(self, operator: str, property: str, value)-> None:
        if self._is_query_empty():
            self._init_query()
        self._query[self._root_key] += [{property: {operator: value}}]

    def reset_query(self) -> None:
        self._query = {}

    @chaineable
    def contained_in(self, property: str, values) -> None:
        self._add_to_query('$in', property, values)

    @chaineable
    def not_contained_in(self, property: str, values) -> None:
        self._add_to_query('$nin', property, values)

    @chaineable
    def lower(self, property: str, value) -> None:
        self._add_to_query('$lt', property, value)

    @chaineable
    def lower_or_equal(self, property: str, value) -> None:
        self._add_to_query('$lte', property, value)

    @chaineable
    def greater(self, property: str, value) -> None:
        self._add_to_query('$gt', property, value)

    @chaineable
    def greater_or_equal(self, property: str, value) -> None:
        self._add_to_query('$gte', property, value)

    @chaineable
    def equal(self, property: str, value) -> None:
        self._add_to_query('$eq', property, value)

    @chaineable
    def not_equal(self, property: str, value) -> None:
        self._add_to_query('$ne', property, value)

    @chaineable
    def contains_text(self, property: str, value) -> None:
        self._add_to_query('$regex', property, value)
