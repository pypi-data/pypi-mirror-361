from wb_api.sync_api import SyncAPI
from wb_api.common.sync_api import SyncCommonAPI
from wb_api.feedback.sync_api import SyncFeedbackAPI
from wb_api.generic.requests.auth import JWTTokenAuth
from wb_api.const import Header

from requests.sessions import Session


class TestSyncAPI:
	def test___init__(self):
		session = Session()
		api = SyncAPI(session)
		assert api.session is session
		assert isinstance(api.common, SyncCommonAPI)
		assert api.common.session is session
		assert isinstance(api.feedback, SyncFeedbackAPI)
		assert api.feedback.session is session

	def test_build(self):
		api = SyncAPI.build("ACCESS_TOKEN")
		assert isinstance(api.session.auth, JWTTokenAuth)
		assert api.session.auth.token == "ACCESS_TOKEN"
		assert api.session.auth.header_label == Header.AUTHORIZATION.value

	def test_make_session(self):
		session = SyncAPI.make_session("ACCESS_TOKEN")
		assert isinstance(session, Session)
		assert isinstance(session.auth, JWTTokenAuth)
		assert session.auth.token == "ACCESS_TOKEN"
		assert session.auth.header_label == Header.AUTHORIZATION.value
