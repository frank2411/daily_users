FROM python:3.9

COPY . code/
WORKDIR "/code"
RUN pip3 install -r requirements.txt

EXPOSE 8090

CMD flask run --host 0.0.0.0 -p 8090
