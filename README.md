#This application reads JSON data from an AWS SQS queue and stores the information in a PostgreSQL database. It masks sensitive information (PII) using SHA-256 hashing before saving it.

1. download the Docker Desktop application for your operating system
2. Create below five files app.py, requirements.txt, Docker File, message.json and docker-compose.yml under one folder
3. Create the python script. Below is the (python script - app.py) Flow Explanation
   a. Import the libraries such as  os, json, datetime, hashlib, boto3, and psycopg2.
   b. A function mask_pii is defined to hash PII using SHA-256.
   c. create_table_if_not_exists function: Create the table user_logins if it doesn't exist in postgres database
   d. Setup sql client and Postgres connection
   e. checks if the specified queue exists; if not, create the queue
   f. For each message:
	- Parses the message body from JSON format.
	- Masks the PII data (IP and device ID) using the mask_pii function.
	- Prepares an SQL INSERT query to insert the message data into the user_logins table.
	- Executes the query to insert data into the database.
	- Deletes the processed message from the SQS queue.
4. Create the requirements.txt which is used in the Dockerfile to install the necessary Python packages inside the container.
5. Create a Docker File. It contains a series of instructions on how to build a Docker image for your application.
6. If you want to orchestrate multiple containers, then you have to set up docker compose yml file. Here I have used three services:
   localstack for AWS SQS emulation
   postgres for PostgreSQL database
   app for application code

   Ports, dependencies, environment variables, and commands are specified
7. message.json content is sent to sqs queue for testing
8. Open command prompt, redirect to your directory, and run the command docker-compose up --build. This starts up all the services, creates the images and        containers
9. Run docker compose ps on other shell to verify whether all the services are running or not
10. Run this command aws --endpoint-url=http://localhost:4566 --region=us-east-1 sqs send-message --queue-url http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/login-queue --message-body file://message.json to send the test data to queue
11. Later verify whether the data is stored on postgres table using the command docker-compose exec postgres psql -d postgres -U postgres -W. 
    Enter the credentials and run the query: select * from user_logins;
12. If you change any code or any file, stop the docker(docker-compose down) and restart the docker
13. The screenshots and a few responses are provided in the Word file
