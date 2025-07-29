# backgroundlog
Thread-based log handler for better performance

![test](https://github.com/diegojromerolopez/backgroundlog/actions/workflows/test.yml/badge.svg)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/diegojromerolopez/backgroundlog/graphs/commit-activity)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/backgroundlog.svg)](https://pypi.python.org/pypi/backgroundlog/)
[![PyPI version backgroundlog](https://badge.fury.io/py/backgroundlog.svg)](https://pypi.python.org/pypi/backgroundlog/)
[![PyPI status](https://img.shields.io/pypi/status/backgroundlog.svg)](https://pypi.python.org/pypi/backgroundlog/)
[![PyPI download month](https://img.shields.io/pypi/dm/backgroundlog.svg)](https://pypi.python.org/pypi/backgroundlog/)

Do not have your python program slowed down by your logging.

## Introduction
Most of the time we log on disk, and all I/O is time consuming.
By leveraging a thread, it is possible to speed up your python application
considerably.

## Use

### Default use

```python
import logging
from backgroundlog.handlers.thread_handler import ThreadHandler

# Setting up the logging thread handler
file_handler = logging.FileHandler('/var/log/myapp.log', mode="a", encoding="utf-8")
thread_handler = ThreadHandler(file_handler)

# Creating a new logger
bg_logger = logging.getLogger('bg_logger')
bg_logger.setLevel(logging.INFO)

# Adding the thread handler
bg_logger.addHandler(thread_handler)

# Using the logger
bg_logger.info('This is a log message')
```

### Options

#### Set a queue size

```python
from backgroundlog.handlers.thread_handler import ThreadHandler

thread_handler = ThreadHandler(file_handler, queue_size=5000)
```

By default, the queue size is 1000.

#### Set a blocking policy by logging record levels

When putting the records in the queue, it could reach the queue size.
We provide a way to deal with this issue: set a blocking policy
by logging record level, and in the case of a non-blocking policy,
the record will be discarded and we will increment a dropped log record.

##### Only info, error and critical records are blocking:

```python
from backgroundlog.handlers.thread_handler import ThreadHandler
from logging import CRITICAL, ERROR, INFO

thread_handler = ThreadHandler(file_handler, blocking_levels={INFO, ERROR, CRITICAL})
```

##### Only error and critical records are blocking

```python
from backgroundlog.handlers.thread_handler import ThreadHandler
from logging import CRITICAL, ERROR

thread_handler = ThreadHandler(file_handler, blocking_levels={ERROR, CRITICAL})
```

##### Only critical records are blocking

```python
from backgroundlog.handlers.thread_handler import ThreadHandler
from logging import CRITICAL

thread_handler = ThreadHandler(file_handler, blocking_levels={CRITICAL})
```

##### No records are blocking

```python
from backgroundlog.handlers.thread_handler import ThreadHandler

thread_handler = ThreadHandler(file_handler, blocking_levels=None)
```

By default, the error and critical records are blocking, the rest are not.

## Performance testing

We have done several local testing with different logging handlers.
See the file
[run_performance_comparison.py](/backgroundlog/performance/run_performance_comparison.py) for
a full catalog of the performance tests we run.

All tests are 100_000 iterations of creating the same logging message,
and were run with Python 3.13.5 in a Macbook Pro M1 with 16 GB of RAM:

| Logging Handler               | Spent Time    |             | vs. Baseline |
|-------------------------------|---------------|-------------|--------------|
|                               | Mean Time (s) | Std Dev (s) |              |
| StreamHandler                 | 0.687         | 0.006       | baseline     |
| FileHandler                   | 0.687         | 0.007       | -0.067%      |
| ThreadHandler (StreamHandler) | 0.477         | 0.003       | -30.646%     |
| ThreadHandler (FileHandler)   | 0.475         | 0.001       | -30.865%     |

As you see there is a ~30% of improvement when running the thread handler.
It is not much, but in some contexts it can be useful for sure.

## Dependencies
This package has no dependencies.

## Python version support
Minimum version support is 3.10.

## License
[MIT](LICENSE) license, but if you need any other contact me.
