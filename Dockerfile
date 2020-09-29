FROM python:alpine3.8
COPY . /app
WORKDIR /app
RUN apk --no-cache add musl-dev gcc postgresql-dev && /app/build.sh
EXPOSE 80 
CMD sh run.sh
