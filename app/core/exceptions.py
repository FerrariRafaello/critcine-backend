# raised by DB layer on unique-constraint violations so services can map it to HTTP 409
class DuplicateEntryError(Exception):
    pass
