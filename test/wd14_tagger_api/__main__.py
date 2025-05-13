import uvicorn
from argparse import ArgumentParser
import os

parser = ArgumentParser(description="Run the Uvicorn server.")
parser.add_argument("-hs", "--host", default="localhost", help="Host to bind")
parser.add_argument("-p", "--port", default=8019, type=int, help="Port to bind")
parser.add_argument("-d", "--device", default="cpu", type=str, help="Device that will be used, you can choose cpu or gpu")
parser.add_argument("-wdm", "--wd14-model", default="wd-v1-4-moat-tagger.v2", type=str, help="first model that will load when you start server")
parser.add_argument("-wdt", "--wd14-threshold", default=0.35, type=float, help="wd-14 Threshold")
parser.add_argument("--replace-underscore",action='store_true',help="Replace underscore to space")

args = parser.parse_args()

os.environ['DEVICE'] = args.device  # Set environment variable for output folder.
os.environ['WD14_MODEL'] = args.wd14_model
os.environ['WD14_THRESHOLD'] = str(args.wd14_threshold)
os.environ['WD14_REPLACE_UNDERSCORE'] = str(args.replace_underscore).lower()

from wd14_tagger_api.server import app

uvicorn.run(app, host=args.host, port=args.port)
