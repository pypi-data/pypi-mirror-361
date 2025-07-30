import psycopg2
from psycopg2.extras import RealDictCursor
from mgmt_config import identity
from .env_helper import EnvHelper

from mgmt_config import logger
env_helper: EnvHelper = EnvHelper()
log_execution = env_helper.LOG_EXECUTION
log_args = env_helper.LOG_ARGS
log_result = env_helper.LOG_RESULT


class TenantHelper:
    def __init__(self):
        self.env_helper = EnvHelper()

    def _create_db_connection(self):
        try:
            user = self.env_helper.POSTGRESQL_USER
            host = self.env_helper.POSTGRESQL_HOST
            dbname = self.env_helper.POSTGRESQL_DATABASE

            access_information = identity.get_token(
                scopes="https://ossrdbms-aad.database.windows.net/.default"
            )
            token = access_information.token
            conn_string = f"host={host} user={user} dbname={dbname} password={token}"
            keepalive_kwargs = {
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 5,
                "keepalives_count": 5,
            }
            conn = psycopg2.connect(conn_string, **keepalive_kwargs)
            logger.info("Connected to Azure PostgreSQL successfully.")
            return conn
        except Exception as e:
            logger.error(f"Error establishing a connection to PostgreSQL: {e}")
            raise

    def create_tenant(self, tenant_name):
        conn = self._create_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO tenants (tenant_name) VALUES (%s) RETURNING tenant_id, tenant_name",
                    (tenant_name,),
                )
                new_tenant = cur.fetchone()
                conn.commit()
                return new_tenant
        finally:
            if conn:
                conn.close()

    def get_tenants(self):
        conn = self._create_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT tenant_id, tenant_name FROM tenants")
                return cur.fetchall()
        finally:
            if conn:
                conn.close()

    def get_users(self):
        conn = self._create_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT DISTINCT user_id FROM conversations")
                return cur.fetchall()
        finally:
            if conn:
                conn.close()

    def link_user_to_tenant(self, user_id, tenant_id):
        conn = self._create_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO user_tenant_links (user_id, tenant_id) VALUES (%s, %s)",
                    (user_id, tenant_id),
                )
                conn.commit()
        finally:
            if conn:
                conn.close()

    def get_user_tenant_links(self):
        conn = self._create_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT user_id, tenant_id FROM user_tenant_links")
                return cur.fetchall()
        finally:
            if conn:
                conn.close() 