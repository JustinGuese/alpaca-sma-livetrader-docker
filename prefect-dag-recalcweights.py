from prefect import Flow
from prefect.tasks.shell import ShellTask
from prefect.schedules import Schedule
from prefect.schedules.clocks import CronClock

schedule = Schedule(clocks=[CronClock("30 05 14 * *")])

task = ShellTask(helper_script="cd /home/justin/docker/alpaca-sma-livetrader-docker")
with Flow("SMAReCalcWeights") as f:
    # both tasks will be executed in home directory
    dockercompose = task(command='docker-compose --file /home/justin/docker/alpaca-sma-livetrader-docker/docker-compose-smacalc.yml up')
    dockercompgen = task(command='docker-compose --file /home/justin/docker/alpaca-sma-livetrader-docker/docker-compose-dockercompgen.yml up')
f.schedule = schedule
f.register(project_name="smalivetrader")