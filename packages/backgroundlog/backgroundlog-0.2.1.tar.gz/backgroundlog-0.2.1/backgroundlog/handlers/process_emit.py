import logging


def process_emit(handler_class, handler_config, record_dict):
    handler = handler_class(**handler_config)
    record = logging.makeLogRecord(record_dict)
    handler.emit(record)
    handler.close()
