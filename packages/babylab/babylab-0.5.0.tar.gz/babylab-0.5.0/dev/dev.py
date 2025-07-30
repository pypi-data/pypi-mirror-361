"""
Fixtures for testing
"""

from babylab.src import api
from babylab.app import create_app
from babylab.app import config as conf
from tests import conftest


token = conf.get_api_key()
records = api.Records(token=token)
data_dict = api.get_data_dict(token=token)
ppt = conftest.create_record_ppt()
apt = conftest.create_record_apt()
que = conftest.create_record_que()
ppt_finput = conftest.create_finput_ppt()
apt_finput = conftest.create_finput_apt()
que_finput = conftest.create_finput_que()
app = create_app(env_="test")
client = app.test_client()
app.config["API_KEY"] = token
