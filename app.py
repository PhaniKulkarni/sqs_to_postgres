import os
import json
from datetime import datetime
import hashlib
import boto3
import psycopg2
from psycopg2.extras import execute_values

# Function to mask PII
def mask_pii(value):
    return hashlib.sha256(value.encode()).hexdigest()

def create_table_if_not_exists(cur):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS user_logins (
        user_id VARCHAR(255),
        device_type VARCHAR(50),
        masked_ip VARCHAR(64),
        masked_device_id VARCHAR(64),
        locale VARCHAR(10),
        app_version VARCHAR(20),
        create_date TIMESTAMP
    );
    """
    cur.execute(create_table_query)

# Read messages from SQS, process and write to Postgres
def main():
    # Setup SQS client for LocalStack
    sqs = boto3.client('sqs',endpoint_url='http://localstack:4566',aws_access_key_id='dummy',aws_secret_access_key='dummy',region_name='us-east-1')
    queue_name = 'login-queue'

    # Ensure the queue exists
    try:
        response = sqs.get_queue_url(QueueName=queue_name)
        queue_url = response['QueueUrl']
    except sqs.exceptions.QueueDoesNotExist:
        response = sqs.create_queue(QueueName=queue_name)
        queue_url = response['QueueUrl']

    # Setup Postgres connection
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME', 'postgres'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres'),
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432')
    )
    cur = conn.cursor()
    create_table_if_not_exists(cur)
    conn.commit()

    while True:
        try:
            response = sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=5
            )

            messages = response.get('Messages', [])
            if not messages:
                continue

            for message in messages:
                body = json.loads(message['Body'])
                user_id = body.get('user_id')
                device_type = body.get('device_type')
                masked_ip = mask_pii(body.get('ip'))
                masked_device_id = mask_pii(body.get('device_id'))
                locale = body.get('locale')
                app_version = body.get('app_version')
                create_date = body.get('create_date')
                if isinstance(create_date, datetime):
                    create_date = create_date.isoformat()

                # Insert into Postgres
                query = """
                INSERT INTO user_logins (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                data = (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)
                cur.execute(query, data)
                conn.commit()

                # Delete processed message
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )

        except Exception as e:
            print(f"Error processing SQS messages: {str(e)}")
            conn.rollback()  # Rollback transaction on error

if __name__ == "__main__":
    main()
