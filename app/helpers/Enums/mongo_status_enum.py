from enum import Enum


class MongoStatusEnum(str, Enum):
    NEW = "NEW"
    QUEUED = "QUEUED"
    ERRORED = "ERRORED"
    INDEXED = "INDEXED"
