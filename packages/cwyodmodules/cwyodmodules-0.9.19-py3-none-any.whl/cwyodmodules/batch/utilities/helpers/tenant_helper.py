from .postgres_db import PostgresDB
from mgmt_config import logger

class TenantHelper:
    def __init__(self):
        self.db = PostgresDB()

    def create_tenant(self, tenant_name):
        query = "INSERT INTO tenants (tenant_name) VALUES (%s) RETURNING tenant_id, tenant_name"
        return self.db.execute_query(query, (tenant_name,), fetch="one", commit=True)

    def get_tenants(self):
        query = "SELECT tenant_id, tenant_name FROM tenants"
        return self.db.execute_query(query, fetch="all")

    def link_user_to_tenant(self, user_id, tenant_id):
        query = "INSERT INTO user_tenant_links (user_id, tenant_id) VALUES (%s, %s)"
        self.db.execute_query(query, (user_id, tenant_id), commit=True)

    def get_user_tenant_links(self):
        query = "SELECT user_id, tenant_id FROM user_tenant_links"
        return self.db.execute_query(query, fetch="all") 