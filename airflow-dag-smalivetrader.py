from datetime import datetime,timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator


default_args = {
    'owner': 'me',
    'start_date': datetime(2020,12,4),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG('airflow_sma_livetrader',
         default_args=default_args,
         schedule_interval='30 14-20 * * *', # utc
         ) as dag:
	dockerstart = BashOperator(task_id='docker_sma_livetrader', bash_command="docker-compose --file /home/justin/docker/alpaca-sma-livetrader-docker/docker-compose.yml up")

dockerstart

