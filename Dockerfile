FROM python:3.10

EXPOSE 5000

WORKDIR /app

COPY requirements.txt .              

RUN pip install -r requirements.txt

COPY . .

CMD ["flask", "run", "--host", "0.0.0.0"]


# --host 0.0.0.0 notes
# -d run as deamon
# -it run in interactive mode

# separate COPY because requirement step will be cached