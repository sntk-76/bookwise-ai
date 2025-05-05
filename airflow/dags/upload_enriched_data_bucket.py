import os
from airflow import DAG
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from datetime import datetime

os.environ['GOOGLE_APPLICATION_CREDENTILAS'] = 'opt/airflow/keys/bookwise-ai-458509-014ab71d8d71.json'

default_args = {
    
    'owner':'airflow',
    'start_date':datetime(2024, 1, 1),
    'retries' : 1
}

with DAG(
    dag_id='upload_enriched_data',
    description='uploading the enriched data to the GCP bucket in enriched data folder',
    default_args=default_args,
    schedule_interval=None,
) as dag :
    upload_file = LocalFilesystemToGCSOperator(
        task_id = 'upload_enriched_data',
        src='/opt/airflow/data/enriched_data.csv',
        dst='enriched/enriched_data.csv',
        bucket='bookwise-ai-458509-bucket'
    )

upload_file    