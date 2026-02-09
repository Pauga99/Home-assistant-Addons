FROM python:3.11-alpine

RUN apk add --no-cache tzdata

COPY rootfs/ /

RUN chmod +x /usr/bin/run.sh

EXPOSE 8099

CMD ["/usr/bin/run.sh"]
