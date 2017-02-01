FROM alpine
RUN apk add --no-cache redis
COPY cli.sh .
ENTRYPOINT ["/bin/sh", "/cli.sh"]
