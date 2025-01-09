class SentimentAnalyzeDto:
    def __init__(self, summary: list[str], sentiment: bool, percentage: str):
        self.summary = summary
        self.voted_up = sentiment
        self.percentage = percentage