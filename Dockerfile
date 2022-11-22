FROM python:3.9.13-slim

WORKDIR /usr/src/app

RUN pip install -U pip
RUN pip install pipenv

COPY [ "Pipfile", "Pipfile.lock",  "./"]

RUN pipenv install --system --deploy

COPY . .

# uvicorn api.main:app --host 0.0.0.0 --port 8000 
CMD [ "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000" ]