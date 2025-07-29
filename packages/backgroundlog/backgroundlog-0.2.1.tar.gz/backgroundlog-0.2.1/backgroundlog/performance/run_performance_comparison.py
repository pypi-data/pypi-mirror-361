import logging
import uuid
from pathlib import Path
from time import time

from backgroundlog.handlers.thread_handler import ThreadHandler

DIR_PATH = Path(__file__).parent
LOGGING_FILE_HANDLER_FILE_PATH = DIR_PATH / "test_file_handler.log"
LOGGING_STREAM_HANDLER_FILE_PATH = DIR_PATH / "test_stream_handler.log"


def main() -> None:
    stream_handler = logging.StreamHandler(
        LOGGING_STREAM_HANDLER_FILE_PATH.open("w"),
    )
    file_handler = logging.FileHandler(
        LOGGING_FILE_HANDLER_FILE_PATH,
        mode="a",
        encoding="utf-8",
    )
    thread_handler_stream_handler = ThreadHandler(stream_handler)
    thread_handler_file_handler = ThreadHandler(file_handler)

    stream_handler_spent_time = __run_performance_test(stream_handler)
    file_handler_spent_time = __run_performance_test(file_handler)
    thread_handler_stream_handler_spent_time = __run_performance_test(
        thread_handler_stream_handler
    )
    thread_handler_file_handler_spent_time = __run_performance_test(
        thread_handler_file_handler
    )

    table = f"""
|       Logging handler          | Spent Time |
|:------------------------------:|:---------------------------:|
|     StreamHandler (file-based) | {stream_handler_spent_time} |
|      FileHandler               | {file_handler_spent_time} |
| ThreadHandler (StreamHandler)  | {thread_handler_stream_handler_spent_time} |
|  ThreadHandler (FileHandler)   | {thread_handler_file_handler_spent_time} |
    """

    print(table)

    __cleanup()


def __run_performance_test(
    handler: logging.Handler, iterations: int = 100_000
) -> float:
    logger = logging.getLogger(f"logger{uuid.uuid4()}")
    logger.setLevel(logging.INFO)
    logger.handlers = []
    logger.addHandler(handler)

    start_time = time()
    for log_index in range(iterations):
        logger.info("Test message")
    return time() - start_time


def __cleanup() -> None:
    LOGGING_FILE_HANDLER_FILE_PATH.unlink()
    LOGGING_STREAM_HANDLER_FILE_PATH.unlink()


if __name__ == "__main__":
    main()
