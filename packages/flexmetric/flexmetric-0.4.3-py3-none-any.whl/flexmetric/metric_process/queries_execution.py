from flexmetric.logging_module.logger import get_logger
logger = get_logger(__name__)

logger.info("query execution")

def execute_clickhouse_command(client, command: str):
    try:
        result = client.query(command)
        row_list = result.result_rows
        column_names = result.column_names
        return row_list,column_names
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return None
def execute_sqlite_query(conn,query):
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        column_names = [desc[0] for desc in cursor.description]
        conn.close()
        return float(result[0]) if result and result[0] is not None else None , column_names
    except Exception as ex:
        logger.error(f"Exception : {ex}")
        return None
    


