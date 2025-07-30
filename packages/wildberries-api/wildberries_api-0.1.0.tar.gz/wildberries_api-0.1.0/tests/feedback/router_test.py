from wb_api.feedback.router import FeedbackRouter


class TestFeedbackRouter:
	def test_ping(self):
		router = FeedbackRouter()
		assert router.ping() == "https://feedbacks-api.wildberries.ru/ping"

	def test_new_feedbacks_questions(self):
		router = FeedbackRouter()
		assert router.new_feedbacks_questions() == "https://feedbacks-api.wildberries.ru/api/v1/new-feedbacks-questions"

	def test_question_count_unanswered(self):
		router = FeedbackRouter()
		assert router.question_count_unanswered() == "https://feedbacks-api.wildberries.ru/api/v1/questions/count-unanswered"

	def test_question_count(self):
		router = FeedbackRouter()
		assert router.question_count() == "https://feedbacks-api.wildberries.ru/api/v1/questions/count"

	def test_question_list(self):
		router = FeedbackRouter()
		assert router.question_list() == "https://feedbacks-api.wildberries.ru/api/v1/questions"

	def test_question_mark_as_read(self):
		router = FeedbackRouter()
		assert router.question_mark_as_read() == "https://feedbacks-api.wildberries.ru/api/v1/questions"

	def test_question_reject(self):
		router = FeedbackRouter()
		assert router.question_reject() == "https://feedbacks-api.wildberries.ru/api/v1/questions"

	def test_question_answer_add(self):
		router = FeedbackRouter()
		assert router.question_answer_add() == "https://feedbacks-api.wildberries.ru/api/v1/questions"

	def test_question_answer_update(self):
		router = FeedbackRouter()
		assert router.question_answer_update() == "https://feedbacks-api.wildberries.ru/api/v1/questions"

	def test_question_get(self):
		router = FeedbackRouter()
		assert router.question_get() == "https://feedbacks-api.wildberries.ru/api/v1/question"

	def test_feedback_count_unanswered(self):
		router = FeedbackRouter()
		assert router.feedback_count_unanswered() == "https://feedbacks-api.wildberries.ru/api/v1/feedbacks/count-unanswered"

	def test_feedback_count(self):
		router = FeedbackRouter()
		assert router.feedback_count() == "https://feedbacks-api.wildberries.ru/api/v1/feedbacks/count"

	def test_feedback_list(self):
		router = FeedbackRouter()
		assert router.feedback_list() == "https://feedbacks-api.wildberries.ru/api/v1/feedbacks"

	def test_feedback_supplier_valuations_get(self):
		router = FeedbackRouter()
		assert router.feedback_supplier_valuations_get() == "https://feedbacks-api.wildberries.ru/api/v1/supplier-valuations"

	def test_feedback_text_report(self):
		router = FeedbackRouter()
		assert router.feedback_text_report() == "https://feedbacks-api.wildberries.ru/api/v1/feedbacks/actions"

	def test_feedback_product_report(self):
		router = FeedbackRouter()
		assert router.feedback_product_report() == "https://feedbacks-api.wildberries.ru/api/v1/feedbacks/actions"

	def test_feedback_answer_add(self):
		router = FeedbackRouter()
		assert router.feedback_answer_add() == "https://feedbacks-api.wildberries.ru/api/v1/feedbacks/answer"

	def test_feedback_answer_update(self):
		router = FeedbackRouter()
		assert router.feedback_answer_update() == "https://feedbacks-api.wildberries.ru/api/v1/feedbacks/answer"

	def test_feedback_order_return(self):
		router = FeedbackRouter()
		assert router.feedback_order_return() == "https://feedbacks-api.wildberries.ru/api/v1/feedbacks/order/return"

	def test_feedback_get(self):
		router = FeedbackRouter()
		assert router.feedback_get() == "https://feedbacks-api.wildberries.ru/api/v1/feedback"

	def test_feedback_archived_list(self):
		router = FeedbackRouter()
		assert router.feedback_archived_list() == "https://feedbacks-api.wildberries.ru/api/v1/feedbacks/archive"
