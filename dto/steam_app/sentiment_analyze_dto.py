class SentimentAnalyzeDto:
    def __init__(self, summary: list[str], sentiment: str, percentage: str):
        self.summary = summary
        self.sentiment = sentiment
        self.percentage = percentage