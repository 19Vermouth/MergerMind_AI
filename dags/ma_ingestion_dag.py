from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.sensors.http_sensor import HttpSensor
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.trigger_rule import TriggerRule
import logging
import sys
import os

sys.path.insert(0, '/opt/airflow/src')

log = logging.getLogger(__name__)

default_args = {
    'owner': 'dealsense',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}


def scrape_deals(**context):
    """Run Scrapy spider to collect M&A deals."""
    import subprocess
    result = subprocess.run(
        ['scrapy', 'crawl', 'ma_deals', '-o', '/tmp/deals.json'],
        cwd='/opt/airflow/scraping',
        capture_output=True,
        text=True
    )
    log.info(f"Scrapy stdout: {result.stdout}")
    if result.returncode != 0:
        log.error(f"Scrapy stderr: {result.stderr}")
        raise RuntimeError(f"Scrapy failed with code {result.returncode}")
    return '/tmp/deals.json'


def load_to_bronze(**context):
    """Load raw scraped data into MinIO bronze layer."""
    import json
    import boto3
    from datetime import datetime

    deals_file = context['ti'].xcom_pull(task_ids='scrape_deals')
    if not deals_file or not os.path.exists(deals_file):
        log.info("No new deals to load")
        return 'No deals scraped'

    with open(deals_file, 'r') as f:
        deals = json.load(f)

    s3 = boto3.client(
        's3',
        endpoint_url=os.getenv('MINIO_ENDPOINT', 'http://minio:9000'),
        aws_access_key_id=os.getenv('MINIO_ROOT_USER', 'minioadmin'),
        aws_secret_access_key=os.getenv('MINIO_ROOT_PASSWORD', 'minioadmin'),
    )

    timestamp = datetime.utcnow().strftime('%Y/%m/%d/%H%M%S')
    for i, deal in enumerate(deals):
        key = f"deals/{timestamp}/deal_{i}.json"
        s3.put_object(
            Bucket=os.getenv('MINIO_BUCKET_RAW', 'dealsense-raw'),
            Key=key,
            Body=json.dumps(deal),
            ContentType='application/json'
        )

    log.info(f"Loaded {len(deals)} deals to MinIO bronze layer")
    return f"Loaded {len(deals)} deals"


def transform_to_silver(**context):
    """Parse bronze layer files and load to PostgreSQL staging."""
    import json
    import boto3
    from datetime import datetime

    s3 = boto3.client(
        's3',
        endpoint_url=os.getenv('MINIO_ENDPOINT', 'http://minio:9000'),
        aws_access_key_id=os.getenv('MINIO_ROOT_USER', 'minioadmin'),
        aws_secret_access_key=os.getenv('MINIO_ROOT_PASSWORD', 'minioadmin'),
    )

    bucket = os.getenv('MINIO_BUCKET_RAW', 'dealsense-raw')
    response = s3.list_objects_v2(Bucket=bucket, Prefix=f"deals/{datetime.utcnow().strftime('%Y/%m/%d')}")

    deals = []
    for obj in response.get('Contents', []):
        data = s3.get_object(Bucket=bucket, Key=obj['Key'])
        deals.append(json.loads(data['Body'].read().decode()))

    if not deals:
        log.info("No deals in bronze layer to transform")
        return 'No deals to transform'

    pg_hook = PostgresHook(postgres_conn_id='dealsense_postgres')
    for deal in deals:
        pg_hook.run("""
            INSERT INTO raw.ma_deals (
                acquirer, target, industry, deal_value_usd,
                announcement_date, deal_status, premium_paid,
                ev_revenue, ev_ebitda, source_url, raw_json
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, parameters=(
            deal.get('acquirer'), deal.get('target'), deal.get('industry'),
            deal.get('deal_value_usd'), deal.get('announcement_date'),
            deal.get('deal_status'), deal.get('premium_paid'),
            deal.get('ev_revenue'), deal.get('ev_ebitda'),
            deal.get('source_url'), json.dumps(deal)
        ))

    log.info(f"Transformed {len(deals)} deals to silver layer")
    return f"Transformed {len(deals)} deals"


def quality_check(**context):
    """Run Great Expectations data quality checks."""
    import great_expectations as gx
    from great_expectations.core import ExpectationSuite

    context_ds = gx.get_context()
    suite = ExpectationSuite(name="dealsense_quality_suite")

    pg_hook = PostgresHook(postgres_conn_id='dealsense_postgres')
    df = pg_hook.get_pandas_df("SELECT * FROM raw.ma_deals LIMIT 1000")

    gx_df = context_ds.get_validator(
        batch_request={"datasource_name": "dealsense", "data_connector_name": "default_runtime_data_connector_name", "data_asset_name": "ma_deals"},
        expectation_suite=suite
    )

    result = gx_df.expect_column_values_to_not_be_null("acquirer")
    result = gx_df.expect_column_values_to_not_be_null("target")
    result = gx_df.expect_column_values_to_be_between("deal_value_usd", min_value=0)
    result = gx_df.expect_column_values_to_not_be_null("announcement_date")

    log.info(f"Quality check passed: {result.success}")
    return result.success


with DAG(
    'ma_ingestion_pipeline',
    default_args=default_args,
    description='M&A data ingestion: scrape → bronze → silver → transform → quality',
    schedule_interval='0 2 * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
) as dag:

    start = EmptyOperator(task_id='start')

    scrape = PythonOperator(
        task_id='scrape_deals',
        python_callable=scrape_deals,
        provide_context=True,
    )

    load_bronze = PythonOperator(
        task_id='load_bronze',
        python_callable=load_to_bronze,
        provide_context=True,
    )

    transform_silver = PythonOperator(
        task_id='transform_silver',
        python_callable=transform_to_silver,
        provide_context=True,
    )

    run_dbt = PostgresOperator(
        task_id='dbt_transform',
        postgres_conn_id='dealsense_postgres',
        sql="SELECT dealsense.dbt_run_models();",
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    quality = PythonOperator(
        task_id='data_quality_check',
        python_callable=quality_check,
        provide_context=True,
    )

    alert_on_failure = EmptyOperator(
        task_id='alert_failure',
        trigger_rule=TriggerRule.ONE_FAILED,
    )

    end = EmptyOperator(
        task_id='end',
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    start >> scrape >> load_bronze >> transform_silver >> run_dbt >> quality
    quality >> [end, alert_on_failure]