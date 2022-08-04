def chaineable(f):
    def wrapper(*args):
        f(*args)
        return args[0]
    return wrapper


class QueryBuilder:
    def __init__(self) -> None:
        self.query = {}
        self._root_key = '$and'

    # db.user.find($and: [ {'the_key': { $exists: true }}, {'the_key': null}])
    # {$and: [{rating: {$lte: 5}}, {rating: {$gt: 3}}, {creator: 'Juan G'}]}

    def _init_query(self):
        self.query = {self._root_key: []}

    def _is_query_empty(self):
        return self._root_key not in self.query

    def _add_to_query(self, operator, property, value):
        if self._is_query_empty():
            self._init_query()
        self.query[self._root_key] += [{property: {operator: value}}]

    def _reset_query(self):
        self.query = {}

    def get_query(self):
        return self.query

    @chaineable
    def contained_in(self, property, values):
        self._add_to_query('$in', property, values)

    @chaineable
    def not_contained_in(self, property, values):
        self._add_to_query('$nin', property, values)

    @chaineable
    def lower(self, property, value):
        self._add_to_query('$lt', property, value)

    @chaineable
    def lower_or_equal(self, property, value):
        self._add_to_query('$lte', property, value)

    @chaineable
    def greater(self, property, value):
        self._add_to_query('$gt', property, value)

    @chaineable
    def greater_or_equal(self, property, value):
        self._add_to_query('$gte', property, value)

    @chaineable
    def equal(self, property, value):
        self._add_to_query('$eq', property, value)

    @chaineable
    def not_equal(self, property, value):
        self._add_to_query('$ne', property, value)

    @chaineable
    def contains_text(self, property, value):
        self._add_to_query('$regex', property, value)
