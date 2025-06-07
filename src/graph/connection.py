"""
Copyright (C) 2025 Roland Spatzenegger

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""

from neo4j import GraphDatabase
from typing import Optional

class Neo4jConnection:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        if self.driver:
            self.driver.close()
    
    def query(self, query: str, parameters: Optional[dict] = None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return list(result)
    
    def write_transaction(self, query: str, parameters: Optional[dict] = None):
        with self.driver.session() as session:
            result = session.execute_write(lambda tx: tx.run(query, parameters))
            return result