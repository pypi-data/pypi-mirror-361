import os, dotenv
from ami_client import AMIClient
from ami_client.operation.action import CoreStatus
from ami_client.operation.event import VarSet, Newexten

dotenv.load_dotenv()

ami_client = AMIClient(
    host=os.environ.get('ASTERISK_HOST', '127.0.0.1'),
    port=int(os.environ.get('ASTERISK_PORT', '5038')),
    Username=os.environ.get('ASTERISK_USER'),
    Secret=os.environ.get('ASTERISK_SECRET'),
    AuthType=os.environ.get('ASTERISK_AUTH_TYPE', 'plain'),  #type: ignore
    Key=os.environ.get('ASTERISK_KEY'),
    Events=os.environ.get('ASTERISK_EVENTS', '').split(','),
    timeout=10,
)
ami_client.add_blacklist([VarSet, Newexten])

def test_connection():
    ami_client.connect()
    assert ami_client.is_connected()
    ami_client.disconnect()

def test_auth():
    ami_client.connect()
    ami_client.login()
    assert ami_client.is_authenticated()
    ami_client.disconnect()

def test_core_status():
    assert CoreStatus().send(ami_client, close_connection=True)
