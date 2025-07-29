# dstm

[![PyPI](https://img.shields.io/pypi/v/dstm)](https://pypi.org/project/dstm/)

A very simple task queue library compatible with AWS SQS or AMQP.

## Examples

```python
from dstm import TaskBackend, task, run_worker

@task(queue="high_priority")
def send_email(recipient: str, content: str):
    ...

send_email.
