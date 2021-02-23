from prefect import Flow
from prefect.tasks.shell import ShellTask
from prefect.schedules import Schedule
from prefect.schedules.clocks import CronClock

schedule = Schedule(clocks=[CronClock("30 14-20 * * 1-5")])

task = ShellTask(helper_script="cd /home/dflucy/docker/alpaca-sma-livetrader-docker")
with Flow("SMALivetrader") as f:
    # both tasks will be executed in home directory
    dockercompose = task(command='docker-compose --file /home/dflucy/docker/alpaca-sma-livetrader-docker/docker-compose.yml up')

f.schedule = schedule
f.register(project_name="smalivetrader")
