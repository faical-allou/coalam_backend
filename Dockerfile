#Download Python from DockerHub and use it
FROM python:3.8.3

#Set the working directory in the Docker container
WORKDIR /code

#Copy the dependencies file to the working directory -- NOT USED ANYMORE
COPY requirements.txt .

# Install pipenv and compilation dependencies
RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Install python dependencies in /.venv
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

#Copy the Flask app code to the working directory
COPY . .

#Run the container
CMD [ "pipenv", "run","python", "./src/app.py" ]