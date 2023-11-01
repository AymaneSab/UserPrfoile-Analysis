import findspark
findspark.init()

import logging
from datetime import datetime
import time
import os
import threading

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, ArrayType, DoubleType
from pyspark.sql.functions import from_json, col, concat, lit

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

from Cassandra import *
from Mongo import *

def setupLogging():
    # Create a directory called 'scrapping' if it doesn't exist
    log_directory = './logs/Spark'
    
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Generate a timestamp for the log file name
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Configure the logging system
    log_file = os.path.join(log_directory, f'{current_time}_scrapping.log')

    return log_file 

def sparkTreatment(topicname, kafka_bootstrap_servers , uri ,loger):
    try:

        loger.info("----------> Loading Packages ")

        packages = [
            "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1",
            "org.mongodb:mongo-java-driver:3.12.11",  # MongoDB Java Driver
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0",  # Spark Kafka Integration
            "com.datastax.spark:spark-cassandra-connector_2.12:3.4.0" 
        ]
        
        # Initialize SparkSession for MongoDB

        spark = SparkSession.builder \
            .appName("Spark Treatment") \
            .config("spark.jars.packages", ",".join(packages)) \
            .getOrCreate()   

        loger.info("----------> Packages Loaded Successfully ")

               
        # Define the schema for randomuser.me data

        schema = StructType([
            StructField("gender", StringType(), True),
            StructField("name", StructType([
                StructField("title", StringType(), True),
                StructField("first", StringType(), True),
                StructField("last", StringType(), True)
            ]), True),
            StructField("location", StructType([
                StructField("street", StructType([
                    StructField("number", IntegerType(), True),
                    StructField("name", StringType(), True)
                ]), True),
                StructField("city", StringType(), True),
                StructField("state", StringType(), True),
                StructField("country", StringType(), True),
                StructField("postcode", IntegerType(), True),
                StructField("coordinates", StructType([
                    StructField("latitude", StringType(), True),
                    StructField("longitude", StringType(), True)
                ]), True),
                StructField("timezone", StructType([
                    StructField("offset", StringType(), True),
                    StructField("description", StringType(), True)
                ]), True),
            ]), True),
            StructField("email", StringType(), True),
            StructField("login", StructType([
                StructField("uuid", StringType(), True),
                StructField("username", StringType(), True),
                StructField("password", StringType(), True),
                StructField("salt", StringType(), True),
                StructField("md5", StringType(), True),
                StructField("sha1", StringType(), True),
                StructField("sha256", StringType(), True),
            ]), True),
            StructField("dob", StructType([
                StructField("date", StringType(), True),
                StructField("age", IntegerType(), True)
            ]), True),
            StructField("registered", StructType([
                StructField("date", StringType(), True),
                StructField("age", IntegerType(), True)
            ]), True),
            StructField("phone", StringType(), True),
            StructField("cell", StringType(), True),
            StructField("id", StructType([
                StructField("name", StringType(), True),
                StructField("value", StringType(), True)
            ]), True),
            StructField("picture", StructType([
                StructField("large", StringType(), True),
                StructField("medium", StringType(), True),
                StructField("thumbnail", StringType(), True)
            ]), True),
            StructField("nat", StringType(), True),
        ])

        loger.info("----------> Schema Setted Scuccefully  ")
        
        # Read data from Kafka topic with configurable Kafka bootstrap servers
        df = spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
            .option("format" , "json") \
            .option("startingOffsets", "earliest") \
            .option("subscribe", f"{topicname}") \
            .load() 
            
        # Deserialize the message value from Kafka (assuming it's in JSON format)
        kafka_stream = df.selectExpr("CAST(value AS STRING)")

        loger.info("----------> Data Consummed From Topic -> Success ")

        # Parse the JSON data with the defined schema
        parsed_data = kafka_stream.select(from_json(kafka_stream.value, schema).alias("data")).select("data.*")
        
        
        filtered_df = parsed_data.filter(
            col("gender").isNotNull() &
            col("name").isNotNull() &
            col("dob").isNotNull() &
            col("location").isNotNull() &
            col("email").isNotNull() &
            col("login").isNotNull() &
            col("phone").isNotNull() &
            col("cell").isNotNull() &
            col("id").isNotNull() &
            col("picture").isNotNull() &
            col("nat").isNotNull()
        )

        loger.info("----------> Data Filtered Scuccefully  ")

                   
        transformed_df = filtered_df.select(
            col("gender"),
            concat(col("name.title"), lit(" "), col("name.first"), lit(" "), col("name.last")).alias("full_name"),
            col("dob.date").alias("birthdate"),
            col("dob.age").alias("age"),
            concat(col("location.street.number"), lit(" "), col("location.street.name")).alias("street"),
            col("location.city").alias("city"),
            col("location.state").alias("state"),
            col("location.country").alias("country"),
            col("location.postcode").alias("postcode"),
            concat(col("location.timezone.offset"), lit(" "), col("location.timezone.description")).alias("timezone"),
            col("email"),
            col("nat").alias("nat")
        )

        loger.info("----------> Schema Transformed  Scuccefully  ")

        
        loger.info("----------> Beggining Spark Treatment  ")

        # Create a thread for saving data to Cassandra
        cassandra_thread = threading.Thread(target=save_to_cassandra, args=(transformed_df,))
        
        # Create a thread for MongoDB aggregation
        mongo_thread = threading.Thread(target=save_to_mongo, args=(transformed_df, "User_Profiles" , uri))
        
        # Start both threads in parallel
        cassandra_thread.start()
        mongo_thread.start()
        
        # Wait for both threads to finish
        cassandra_thread.join()
        mongo_thread.join()


        loger.info("Streaming Query Finixhed Successfully")

    except ValueError as ve:
        loger.error("ValueError: %s", ve)
        
    except Exception as e:
        # Log the error with a meaningful message
        loger.error("An error occurred: %s", str(e))

def runSparkTreatment(topic_name, kafka_bootstrap_servers , keyspace_name ,table_name , uri):
    try:
        # Run the keysape creation : 
        
        log_file = setup_logging()

        runCassandraPreparation(keyspace_name, table_name)
        sparkTreatment(topic_name, kafka_bootstrap_servers , uri , log_file) 
        
    except KeyboardInterrupt:
        log_file.info("Spark Treatment Stopped")
    except Exception as e:
        log_file.error(f"An unexpected error occurred: {e}")
        log_file.exception("An unexpected error occurred in Spark")

keyspace_name = "youcode"
table_name = "user"
topic_name = "user_profiles"                         
kafka_bootstrap_servers = "localhost:9092"
uri = "mongodb://localhost:27017/"

runSparkTreatment(topic_name ,kafka_bootstrap_servers , keyspace_name  ,table_name , uri)
