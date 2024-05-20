from fastapi import FastAPI
from routes import user
import os
import logging
from logging.handlers import TimedRotatingFileHandler


app = FastAPI()

app.include_router(user.router, prefix="/api", tags=["user"])

TAIL_PATH = "logs"
FILE_NAME = "integration-be.log"

log_path = os.path.join(os.getcwd(), TAIL_PATH)
simple_logger = logging.getLogger("log")
if not os.path.exists(log_path):
    os.makedirs(log_path)
log_formatter = logging.Formatter(
    '%(asctime)s - %(pathname)20s:%(lineno)4s - %(funcName)20s() - %(levelname)s ## %(message)s')
handler = TimedRotatingFileHandler(log_path + "/" + FILE_NAME,
                                   when="d",
                                   interval=1,
                                   backupCount=10)
handler.setFormatter(log_formatter)
if not len(simple_logger.handlers):
    simple_logger.addHandler(handler)
simple_logger.setLevel(logging.DEBUG)

app.state.logger = simple_logger


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
