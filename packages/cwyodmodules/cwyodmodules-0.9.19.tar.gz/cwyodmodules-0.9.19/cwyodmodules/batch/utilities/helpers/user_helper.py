from .postgres_db import PostgresDB
from mgmt_config import logger

class UserHelper:
    def __init__(self):
        self.db = PostgresDB()

    def get_users(self):
        query = "SELECT DISTINCT user_id FROM conversations"
        return self.db.execute_query(query, fetch="all")

    def get_user_tenant_links(self):
        query = "SELECT user_id, tenant_id FROM user_tenant_links"
        return self.db.execute_query(query, fetch="all") 