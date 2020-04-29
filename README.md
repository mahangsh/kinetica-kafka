# Kinetica Kafka Connector: How-To Guide

The following document provides a step-by-step guide for integrated Kinetica with Kafka and provides a Kafka producer script for generating data into a Kaka topic that is streamed into a table on the Kinetica database.

You should should be able to follow these steps in sequence to get up and running with Kinetica's Kafka Connector, and the same configuration will work with Confluent Kafka as well.

### Prerequisites

- Git
- Kinetica version 7.0.15 or higher
- Apache Kafka (latest)
- Apache Maven (latest)
- OpenJDK 8
- Docker

Make sure you have Apache Kafka and Maven downloaded and installed on your machine
You will need a Java 8 SDK installed as well to build the connector with Maven
Instructions are not provided in this doc for installing Docker, Kafka, Maven, or Java

### The following instructions are for MacOS or Linux based systems

1. Create a Kinetica Docker Container
   
    ```
    docker run \
      -p 8080:8080 -p 8088:8088 -p 9191:9191 -p 9002:9002 \
      --name kinetica \
      -d kinetica/kinetica-intel:latest
    ```


2. Activate and Start Kinetica
    
    1. Log into the container on KAdmin UI --> http://localhost:8080
        ```
        username = admin
        password = admin
        ```

    2. Add the license key and save the configuration
        ```
        ldw5jxnG5e+v-yyQ3EsdCXRwV-TXRaXYIjAfp4-IU/YKVxP3IXU-2FRNraSqerpqt9RJUtzAUU4hhwi4kp5L
        ```

    3. Start the Database service

3. Download and Unzip Kafka
   1. Download Apache Kafka --> https://kafka.apache.org/downloads.html
   2. Unzip the downloaded zip file to a folder you have rights to

      `Example on Mac: /Users/<user_name>/`

   3. Set KAFKA_HOME environment variable
      ```
      export KAFKA_HOME=/Users/<user_name>/kafka_2.12-2.5.0
      ```
4. Clone and Build the Kafka Connector

    1. Clone the repo
        ```
        git clone https://github.com/kineticadb/kinetica-connector-kafka.git
        ```

    2. Change into the cloned directory
        ```
        cd kinetica-connector-kafka
        ```
    3. Update the `pom.xml` with the JDK and Kafka versions to the one matching your Kafka download and JDK version.

        Example: 
        ```
        <java.version>1.8</java.version>
        <kafka.version>2.5.0</kafka.version>
        ```
    4. Build the Kafka Connector
        ```
        mvn clean package -DskipTests
        ```

5. Copy Kafka Connector JAR to KAFKA_HOME
    ```
    cp kafka-<KAFKA_VERSION>-connector-kinetica-7.0.1.3-jar-with-dependencies.jar $KAFKA_HOME/libs
    ```
    Example:
    ```
    cp kafka-2.5.0-connector-kinetica-7.0.1.3-jar-with-dependencies.jar $KAFKA_HOME/libs
    ```
6. Create `kinetica` folder in `config` directory where you installed Kafka to store the kinetica properties files
    
    1. Create directory
      ```
      mkdir $KAFKA_HOME/config/kinetica
      ```

    2. Copy or create the config files in KAFKA_HOME/config/kinetica
        
        Configs are available in the `target` directory of the Maven build, or you can use the ones cloned from this repo.

        For example:
        ```
        cp <REPO>/configs/
        ```
    3.  Edit the `connect-standalone.properties` file so that they configuration has these settings:
        ```
        key.converter=org.apache.kafka.connect.storage.StringConverter
        value.converter=org.apache.kafka.connect.json.JsonConverter
        ```

7. Create table in Kinetica with the following Schema & Data

    Table Name = `movie_ratings`
    ```
    userId|long,movieId|long,rating|float,ts|long|timestamp
    1,2,3.5,1112486027
    ```
8. Start Zookeeper & Kafka

    1. Go the the folder where Kafka is installed
        ```
        cd $KAFKA_HOME
        ```
    2. Start **Zookeeper** (process will run in the background)
        ```
        bin/zookeeper-server-start.sh config/zookeeper.properties &
        ```
    3. Start **Kafka** (process will run in the background)
        ```
        bin/kafka-server-start.sh config/server.properties &
        ```

9. Create a Kafka Topic
    ```
    bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic movie_ratings
    ```
10. Verify that the topic was created:
    ```
    bin/kafka-topics.sh --list --bootstrap-server localhost:9092
    ```
11. Start the Kinetica Kafka connectors
    ```
    bin/connect-standalone.sh \
    config/connect-standalone.properties  \
    config/kinetica/quickstart-kinetica-sink.properties
    ```

Optionally, you can start the Source and Sink connectors together, but you need to ensure that your table already exists before the source connector is able to read data from it--otherwise, the source connector will terminate.
```
bin/connect-standalone.sh \
config/connect-standalone.properties  \
config/kinetica/quickstart-kinetica-sink.properties \
config/kinetica/quickstart-kinetica-source.properties
```

12. Copy or move the sample data and the Python stream producer to a desired location

    Make sure the python app and the sample data files are located in the same directory.

    A new record will be streamed to the Kafka topic every 1/2 second.

    Start the data sreaming python app
    ```
    #install the kafka library if it's not already installed
    pip3 install kafka-python

    python3 stream_data.py
    ```