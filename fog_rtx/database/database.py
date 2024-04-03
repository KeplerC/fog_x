from abc import ABC, abstractmethod


class DatabaseConnector(ABC):
    @abstractmethod
    def add(self, row):
        pass

    @abstractmethod
    def query(self, key):
        pass

    @abstractmethod
    def close(self):
        pass


class DatabaseManager:
    def __init__(self, database: DatabaseConnector):
        self.database = database

    def add(self, feature, value):
        # self.database.add(row)
        pass

    def query(self, key):
        return self.database.query(key)

    def close(self):
        self.database.close()
