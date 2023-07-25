from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv("TOKEN")
contract_addr = os.getenv("CONTRACT")