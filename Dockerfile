# syntax=docker/dockerfile:1
ARG FLAVOR=${FLAVOR:-"bullseye"}
ARG ARCH=${ARCH:-"amd64"}

FROM $ARCH/python:$FLAVOR AS build
ARG TARGET_HOST=${TARGET_HOST:-"x86_64-pc-linux-gnu"}

RUN mkdir -p work/wheels
COPY . /work
WORKDIR /work
RUN python3 -m pip install requests cython
RUN ./build.sh --host=$TARGET_HOST --docker

FROM scratch as artifact
COPY --from=build /work/src/wheels ./wheels

FROM release
