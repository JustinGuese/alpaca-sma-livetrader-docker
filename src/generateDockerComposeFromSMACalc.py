START = 'version: "3"\nservices:'
block = '''  smatrader%s:
    container_name: smatrader%s
    image: smaalpacatrader:latest
    build: ./src
    command: bash -c "python predictor.py"
    env_file:
      - .alpacalogin
    environment: 
      - STOCK=%s
      - FastSMA=%s
      - SlowSMA=%s
      - MoneyDivide=%s
    network_mode: "host"

'''

def writeEntry(stock,fast,slow,nrfiles):
    global block,START
    tmp = block % (stock.lower(),stock.lower(),stock,fast,slow,nrfiles)
    START += tmp

import glob

nrfiles = len(glob.glob("./output/"+'*.csv'))
for file_name in glob.glob("./output/"+'*.csv'):
    with open(file_name) as f:
        line = f.readline()
        stock,fast,slow,sqn,ret = line.split(",")
        writeEntry(stock,fast,slow,nrfiles)
        #print(stock,fast,slow,nrfiles)

with open("./docker-compose.yml","w") as f:
    f.write(START)
print(START)