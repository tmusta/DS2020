FROM ubuntu:18.04

MAINTAINER toni_musta_2497530

RUN apt-get -qq -y update && apt-get -y install python3 python3-pip

RUN pip3 install requests numpy 