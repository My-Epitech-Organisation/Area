FROM alpine:3.20

RUN mkdir -p /apk
VOLUME ["/apk"]

CMD ["sh", "-lc", "echo 'stub apk' > /apk/client.apk && sleep 3600"]
