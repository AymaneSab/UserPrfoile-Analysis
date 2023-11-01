import os
import json
import logging
import time
import datetime
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from Scrapper import scrappUsers

def setup_producer_logging():
    log_dir = "./logs/Producer_Log_Files"
    
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_filename = f"{log_dir}/{datetime.datetime.now().strftime('%Y-%m-%d')}_producer.log"

    producer_logger = logging.getLogger("producer")
    producer_logger.setLevel(logging.INFO)
    
    producer_handler = logging.FileHandler(log_filename)
    producer_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    producer_handler.setFormatter(producer_formatter)
    
    producer_logger.addHandler(producer_handler)

    return producer_logger

def create_kafka_topic(topic, admin_client, producer_logger):
    try:
        topic_name = topic
        topic_spec = NewTopic(topic, num_partitions=1, replication_factor=1)

        admin_client.create_topics([topic_spec])

        producer_logger.info(f" Topic ----{topic}----- Created Successfully: ")

    except Exception as e:
        error_message = "Error creating Kafka topic: " + str(e)
        producer_logger.error(error_message)

def produce_to_kafka(topic, producer_logger):
    try:
        # Create a Kafka admin client
        admin_client = AdminClient({"bootstrap.servers": "localhost:9092"})

        # Check if the topic exists, and create it if not
        existing_topics = admin_client.list_topics().topics

        if topic not in existing_topics:
            create_kafka_topic(topic, admin_client, producer_logger)
            print(f"Kafka topic '{topic}' created.")

        producer = Producer({"bootstrap.servers": "localhost:9092"})  # Kafka broker address

        while True:
            user = scrappUsers()  
            user_json = json.dumps(user)  # Convert the dictionary to a JSON-formatted string

            producer.produce(topic, key="user", value=user_json)
            producer.flush()    
            
            producer_logger.info("User Produced Successfully: ")     

            time.sleep(5)

    except Exception as e:
        producer_logger.error("Error producing to Kafka: " + str(e))

def runKafkaProducer(topic_name):
    try:
        producer_logger = setup_producer_logging()

        topic = topic_name
        current_datetime = datetime.datetime.now()

        produce_to_kafka(topic, producer_logger)
        
    except KeyboardInterrupt:
        producer_logger.info("Kafka Producer Stopped")

    except Exception as e:
        producer_logger.error("An unexpected error occurred in Kafka Producer: " + str(e))

topic = "user_profiles"
runKafkaProducer(topic)