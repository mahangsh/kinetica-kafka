from json import dumps
from kafka import KafkaProducer
import csv, time

FILE_PATH="../data/movie_ratings_sample_10K.csv"
KAFKA_TOPIC="movie_ratings"
PAUSE=1
SKIP_HEADER=True

producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         #batch_size=100000,
                         value_serializer=lambda x: dumps(x).encode('utf-8'))
with open(FILE_PATH) as csv_file:
    input = csv.reader(csv_file, delimiter=',')
    if SKIP_HEADER:
        next(input)
    for record in input:
        data = {   
                    'userID': int(record[0]), 
                    'movieID': int(record[1]), 
                    'rating': float(record[2]), 
                    'ts': int(record[3])
                }
        print("Sending data to Kafka", data)
        producer.send(KAFKA_TOPIC, value=data)
        producer.flush()
        time.sleep(PAUSE)
