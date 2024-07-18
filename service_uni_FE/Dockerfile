# Use the official Python image from the Docker Hub

FROM python:3.8.2

# Make a new directory to put our code in.

RUN mkdir /code

# Change the working directory.

WORKDIR /code

# Copy to code folder

COPY . /code/

# Install the requirements.

RUN pip install -r requirements.txt

#ENTRYPOINT ["/code/docker-entrypoint.sh"]
# Run the application:

CMD python -u manage.py runserver 0.0.0.0:8005

#CMD ["python", "-u", "manage.py", "runserver", " 0.0.0.0:8005"]