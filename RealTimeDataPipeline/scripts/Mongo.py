from pyspark.sql import SparkSession
from pyspark.sql.functions import substring_index, col, count, avg , count, substring_index
from pymongo import MongoClient
from datetime import datetime
import logging
import os


def setup_logging():
    log_dir = "./logs/Mongo"
    
    try:
        # Create the log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Create a log file with the current date and time
        log_file = os.path.join(log_dir, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        return log_file

    except OSError as e:
        print(f"Error creating log directory: {str(e)}")

def setup_checkpoint_directory(checkpoint_dir , log_file):
    try:
        os.makedirs(checkpoint_dir, exist_ok=True)
    except OSError as e:
        log_file.error(f"Error creating checkpoint directory: {str(e)}")

def save_to_mongodb_collection(data_frame, collection_name, db_name , uri , log_file):
    try:

        # client = MongoClient("mongodb://localhost:27017/")
        client = MongoClient(uri)

        # Select the database or create it if it doesn't exist
        db = client[db_name]

        # Dynamically create the collection if it doesn't exist
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)

        # Save the DataFrame to the specified collection in MongoDB
        data_frame.write \
            .format("com.mongodb.spark.sql.DefaultSource") \
            .option("uri", uri) \
            .option("database", db_name) \
            .option("collection", collection_name) \
            .mode("append") \
            .save()
        
        log_file.info(f"Data saved to MongoDB collection '{collection_name}' in database '{db_name}'.")

        
        # Close the MongoDB client
        client.close()

    except Exception as e:
        logging.error(f"An error occurred while saving data to MongoDB: {str(e)}")

def save_to_mongo(transformed_df, db_name , uri):
    log_file =  setup_logging()
    try:
        # Create a MongoDB client
        client = MongoClient(uri)
        
        # Create a database if it doesn't exist
        db = client[db_name]

        # Define a function to process and save data to MongoDB
        def process_and_save_to_mongodb(df, epoch_id):
            try:
                # Calculate the average age of users
                avg_age_df = df.selectExpr("avg(age) as avg_age")
                # Count the number of users by nationality
                nationality_count_df = df.groupBy("Nat").agg(count("*").alias("user_count"))

                # Extract and count the most common email domains
                email_domain_df = df.select(
                    substring_index(col("email"), "@", -1).alias("email_domain")
                ).groupBy("email_domain").agg(count("*").alias("domain_count"))


                # Save the aggregated data to MongoDB collections
                save_to_mongodb_collection(avg_age_df, "average_age", db_name , uri , log_file)
                save_to_mongodb_collection(nationality_count_df, "user_count_by_nationality", db_name , uri , log_file)
                save_to_mongodb_collection(email_domain_df, "common_email_domains", db_name , uri , log_file)

                log_file.info(f"Data saved to MongoDB collection in database '{db_name}'.")

            except Exception as e:
                log_file.error(f"An error occurred during aggregation: {str(e)}")

        # Define your checkpoint directory
        checkpoint_dir = "./mongoDB/checkpoint/Data"

        # Create the checkpoint directory if it doesn't exist
        setup_checkpoint_directory(checkpoint_dir , log_file)

        # Use foreachBatch to process the DataFrame in batches
        query = transformed_df.writeStream \
            .outputMode("append") \
            .option("checkpointLocation", checkpoint_dir) \
            .foreachBatch(process_and_save_to_mongodb) \
            .start()
        
        # Wait for the query to terminate
        query.awaitTermination()

        log_file.info(f"Data Aggregated Successfully To MongoDB in database '{db_name}'")

    except Exception as e:
        log_file.error(f"An error occurred during aggregation: {str(e)}")


