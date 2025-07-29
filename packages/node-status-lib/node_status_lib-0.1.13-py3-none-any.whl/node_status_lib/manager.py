import json
from db import get_db_connection
from enums import Status

class NodeStatusManager:
    def __init__(self, node_id: str, node_name: str, flows: list[str], db_details=dict):
        self.conn = get_db_connection(
            db_name=db_details.get("DB_NAME"),
            db_user=db_details.get("DB_USER"),
            db_password=db_details.get("DB_PASSWORD"),
            db_host=db_details.get("DB_HOST"),
            db_port=db_details.get("DB_PORT", "5432")
        )
        self.node_id = node_id
        self.node_name = node_name
        self._init_node(flows)

    def _init_node(self, flows: list[str]):
        initial_flows = {flow: Status.NOT_RUNNING.value for flow in flows}
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO node_status (node_id, node_name, node_status, flow_status, last_updated)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (node_id) DO UPDATE SET
                    node_name = EXCLUDED.node_name,
                    node_status = EXCLUDED.node_status,
                    flow_status = EXCLUDED.flow_status,
                    last_updated = CURRENT_TIMESTAMP;
            """, (self.node_id, self.node_name, Status.NOT_RUNNING.value, json.dumps(initial_flows)))
            self.conn.commit()

    def update_node_status(self, status: Status):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE node_status
                SET node_status = %s,
                    last_updated = CURRENT_TIMESTAMP
                WHERE node_id = %s;
            """, (status.value, self.node_id))
            self.conn.commit()

    def update_flow_status(self, flow_name: str, status: Status):
        with self.conn.cursor() as cur:
            # Load current flow_status JSON
            cur.execute("SELECT flow_status FROM node_status WHERE node_id = %s;", (self.node_id,))
            result = cur.fetchone()
            if not result:
                raise ValueError("Node not found.")
            flow_status = result[0]
            flow_status[flow_name] = status.value  # Update the specific flow

            # Update only the JSON field
            cur.execute("""
                UPDATE node_status
                SET flow_status = %s,
                    last_updated = CURRENT_TIMESTAMP
                WHERE node_id = %s;
            """, (json.dumps(flow_status), self.node_id))
            self.conn.commit()
