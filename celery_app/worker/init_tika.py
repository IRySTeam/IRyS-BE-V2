# Init tika server
import tika
from tika import parser

print("Trying to init tika server")

tika.initVM()

tika_started = False

while not tika_started:
    try:
        with open("./celery_app/worker/init_tika.pdf", "rb") as f:
            parser.from_file(f)
        tika_started = True
    except:
        pass

print("Tika server is ready")
