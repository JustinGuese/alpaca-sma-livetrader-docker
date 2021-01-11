FROM python:3.8
RUN mkdir -p output
COPY predictor.py /
COPY smacalculator.py /
COPY requirements.txt / 
COPY generateDockerComposeFromSMACalc.py /
RUN pip install -r requirements.txt