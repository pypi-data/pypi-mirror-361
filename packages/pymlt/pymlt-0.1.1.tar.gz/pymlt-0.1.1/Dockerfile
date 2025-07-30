FROM python:3.12-slim

# update pip
RUN python -m pip install --upgrade pip

# install uv
RUN pip install uv

# copy the scripts from the local directory to the container
# note: pymlt package is installed via uv from pypi
COPY ./ /app/

# set the working directory in the container
WORKDIR /app

# set the environment variable
ENV PYTHONPATH="/app"

# install package
RUN uv sync --all-groups

# Default command
ENTRYPOINT ["python", "-u"]
CMD ["scripts/train.py"]