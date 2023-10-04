from fluent import asyncsender as sender

# https://github.com/fluent/fluent-logger-python

f_logger = sender.Fluentsender('alexandria', host='host', port=24224)


