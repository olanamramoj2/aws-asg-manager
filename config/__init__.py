from dotenv import load_dotenv
import os


load_dotenv(verbose=True)

INSTANCE_ID = os.getenv('INSTANCE_ID')
AMI_NAME = os.getenv('AMI_NAME')
INSTANCE_TYPE = os.getenv('INSTANCE_TYPE')
SPOT_PRICE = os.getenv('SPOT_PRICE')
USER_DATA = os.getenv('USER_DATA')
INSTANCE_VOLUME_SIZE = os.getenv('INSTANCE_VOLUME_SIZE')
BLOCK_DEVICE = os.getenv('BLOCK_DEVICE')
LAUNCH_CONFIG_NAME = os.getenv('LAUNCH_CONFIG_NAME')
SECURITY_GROUPS = os.getenv('SECURITY_GROUPS')
ASG_NAME = os.getenv('ASG_NAME')
MIN_ASG_SIZE = os.getenv('MIN_ASG_SIZE')
MAX_ASG_SIZE = os.getenv('MAX_ASG_SIZE')
BACKUP_RETENTION_IN_DAYS = int(os.getenv('BACKUP_RETENTION_IN_DAYS'))
EC2_KEYNAME = os.getenv('EC2_KEYNAME')
DETAILED_MONITORING = bool(int(os.getenv('DETAILED_MONITORING')))
INSTANCE_PROFILE = os.getenv('INSTANCE_PROFILE')
VOLUME_TYPE = os.getenv('VOLUME_TYPE')