FROM golang:alpine3.9

RUN apk add git
#RUN apk add gcc

RUN go version
RUN CGO_ENABLED=0 go get -v github.com/apache/mynewt-mcumgr-cli/mcumgr

