
from datetime import timedelta
import pendulum

# Define the timezone for operations
TIMEZONE = pendulum.timezone("Asia/Seoul")

# Various time intervals as timedelta objects
TIME_30S = timedelta(seconds=30)
TIME_1M = timedelta(minutes=1)
TIME_2M = timedelta(minutes=2)
TIME_3M = timedelta(minutes=3)
TIME_4M = timedelta(minutes=4)
TIME_5M = timedelta(minutes=5)
TIME_10M = timedelta(minutes=10)
TIME_15M = timedelta(minutes=15)
TIME_30M = timedelta(minutes=30)
TIME_1H = timedelta(hours=1)
TIME_2H = timedelta(hours=2)
TIME_3H = timedelta(hours=3)
TIME_6H = timedelta(hours=6)

# Default arguments for Airflow tasks
DEFAULT_ARGS = {
    "owner": "airflow",                                # DAG Owner.
    "email": [],                                       # Email addresses to receive alerts.
    "email_on_failure": True,                          # Whether to send email on task failure.
    "email_on_retry": False,                           # Whether to send email on retry.
    "retries": 3,                                      # Maximum number of retries.
    "retry_delay": TIME_2M,                            # Interval between retries.
    #"execution_timeout": TIME_6H,                     # Maximum execution time for the DAG.
    # "pool": "default_pool",                          # Pool to use for task execution.
    # "trigger_rule": "all_success"                    # Rule to trigger tasks.
    # "queue": "bash_queue",                           # Queue to use for task execution.
    # "priority_weight": 10,                           # Priority weight of the task.
    # "end_date": datetime(2016, 1, 1),                # End date for the task execution.
    # "wait_for_downstream": False,                    # Whether to wait for downstream tasks to complete.
    # "dag": dag,                                      # DAG to which the task belongs.
    # "sla": timedelta(hours=2),                       # Service level agreement time.
    # "on_failure_callback": some_function,            # Function to call on task failure.
    # "on_success_callback": some_other_function,      # Function to call on task success.
    # "on_retry_callback": another_function,           # Function to call on task retry.
    # "sla_miss_callback": yet_another_function,       # Function to call on SLA miss.
}

