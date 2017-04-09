FROM alpine
RUN apk add --no-cache less groff python3 && \
    pip3 install awscli
VOLUME /root/.aws
ENTRYPOINT ["aws"]
