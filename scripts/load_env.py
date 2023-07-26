from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv("TOKEN")
contract_addr = os.getenv("CONTRACT")
allowed_role = os.getenv("ALLOWED_ROLE")