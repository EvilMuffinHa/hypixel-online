FROM python

ADD /ho /ho/

WORKDIR /ho/

RUN pip install --upgrade -r requirements.txt

CMD [ "python3", "main.py" ]