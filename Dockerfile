FROM ubuntu

WORKDIR /architecture_patterns

RUN apt update

RUN apt-get install -y python3 python3-pip

RUN pip install pipenv

# COPY Pipfile Pipfile.lock ./

COPY . .

ENV LANG="C.UTF-8"

RUN pipenv install -e .

# RUN pipenv shell

ENTRYPOINT ["tail", "-f", "/dev/null"]