import logging
import os
from datetime import datetime

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, ArrayType, DoubleType
from pyspark.sql.functions import from_json, col, concat, lit

class CassandraConnector:
    def __init__(self, username, password, hosts):
        self.username = username
        self.password = password
        self.hosts = hosts
        self.session = None
        self.cluster = None

    def connect(self):
        auth_provider = PlainTextAuthProvider(username=self.username, password=self.password)
        self.cluster = Cluster(self.hosts, auth_provider=auth_provider)
        self.session = self.cluster.connect()

    def close(self):
        if self.session:
            self.session.shutdown()
        if self.cluster:
            self.cluster.shutdown()

def setup_logging(log_dir):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_filename = f"{log_dir}/{datetime.now().strftime('%Y-%m-%d')}.log"

    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    return log_filename

def create_cassandra_keyspace(connector, keyspace):
    try:
        # Initialize the Cassandra connector
        connector.connect()

        # CQL to create a new keyspace
        create_keyspace_cql = f"CREATE KEYSPACE IF NOT EXISTS {keyspace} WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}"

        # Execute the CQL statement
        connector.session.execute(create_keyspace_cql)

        logging.info("Cassandra KeySpace Created Successfully")

    except Exception as e:
        logging.error(f"An error occurred while creating the keyspace: {str(e)}")

    finally:
        connector.close()

def create_cassandra_table(connector, keyspace, table_name):
    try:
        connector.connect()

        # Set the keyspace
        connector.session.execute(f"USE {keyspace}")

        # Define the schema columns and data types explicitly
        create_table_cql = f"""
            CREATE TABLE IF NOT EXISTS {keyspace}.{table_name} (
                gender text,
                full_name text,
                birthdate text,
                age int,
                street text,
                city text,
                state text,
                country text,
                postcode int,
                timezone text,
                email text,
                Nat text,  
                PRIMARY KEY (email)
            )
        """

        # Execute the CQL statement to create the table in the specified keyspace
        connector.session.execute(create_table_cql)

        logging.info("Cassandra Table Created Successfully")

    except Exception as e:
        logging.error(f"An error occurred while creating the Cassandra table: {str(e)}")

    finally:
        connector.close()

def write_to_cassandra(batch_df, batch_id):
    try:
        # Configure Cassandra settings
        kafka_bootstrap_servers = "localhost:9092"
        cassandra_keyspace = "youcode"  # Your Cassandra keyspace
        cassandra_table = "user"  # Your Cassandra table

        # Write the batch DataFrame to Cassandra
        batch_df.write \
            .format("org.apache.spark.sql.cassandra") \
            .options(table=cassandra_table, keyspace=cassandra_keyspace, cluster=kafka_bootstrap_servers) \
            .mode("append") \
            .save()

        # Log a success message
        logging.info(f"Batch {batch_id} successfully written to Cassandra.")

    except Exception as e:
        # Handle exceptions, e.g., log the error and take appropriate action
        logging.error(f"Error writing batch {batch_id} to Cassandra: {str(e)}")
        
def runCassandraPreparation(keyspace, table):
    try:
        log_file = setup_logging("./logs/Cassandra/Env_Preparation")

        # Initialize the Cassandra connector
        cassandra_connector = CassandraConnector('cassandra', 'cassandra', ['localhost'])

        create_cassandra_keyspace(cassandra_connector, keyspace)
        create_cassandra_table(cassandra_connector, keyspace, table)

    except KeyboardInterrupt:
        logging.info("Cassandra Insertion Stopped")

    except Exception as e:
        logging.error(f"An unexpected error occurred in Cassandra Insertion: {e}")

def save_to_cassandra(transformed_df):
        
        query = transformed_df.writeStream \
            .outputMode("append") \
            .foreachBatch(write_to_cassandra) \
            .start()
        
            
        logging.info("Streaming Query Finixhed Successfully")

        # Log success message
        query.awaitTermination()