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