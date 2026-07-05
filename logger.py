import logging
import os
from config import LOG_FOLDER
os.makedirs(LOG_FOLDER, exist_ok=True)
LOG_FILE = os.path.join(LOG_FOLDER,"agentic_rag.log")

logging.basicConfig(filename=LOG_FILE,level=logging.INFO,format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)