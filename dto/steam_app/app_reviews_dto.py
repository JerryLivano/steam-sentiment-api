class AppReviewsDto:
    def __init__(self, voted_up: bool, review: str):
        self.voted_up = voted_up
        self.review = review
