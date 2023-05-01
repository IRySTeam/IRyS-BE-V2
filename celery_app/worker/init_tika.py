# Init tika server
import tika
from tika import parser

print("Trying to init tika server")

tika.initVM()

with open("./celery_app/worker/init_tika.pdf", "rb") as f:
    parser.from_file(f)

print("Tika server is ready")
