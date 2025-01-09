import requests
import pandas as pd
import nltk
import re
import time
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score
from sklearn.decomposition import LatentDirichletAllocation
from googletrans import Translator
from textblob import TextBlob
from collections import Counter
from nltk.util import ngrams
from dto.steam_app.sentiment_analyze_dto import SentimentAnalyzeDto
nltk.download('punkt_tab')
nltk.download("stopwords")

class SentimentAnalysisService:
    @staticmethod
    def clean_html_regex(text):
        clean_text = re.sub(r'\[.*?\]', '', text)
        clean_text = re.sub(r'[\*\/*\\]', '', clean_text)
        clean_text = re.sub(r'\s+', ' ', clean_text)
        return clean_text.strip()

    @staticmethod
    def translate_to_english(text, translator):
        if not text or not isinstance(text, str):
            return text
        try:
            translation = translator.translate(text, src='auto', dest='en')
            return translation.text
        except Exception as e:
            return text

    def fetch_reviews(self, app_id, max_reviews=1000, num_per_page=100, delay=1):
        url = f"https://store.steampowered.com/appreviews/{app_id}?json=1&num_per_page={num_per_page}"
        all_reviews = []
        seen_reviews = set()
        cursor = "*"
        total_fetched = 0

        translator = Translator()

        while total_fetched < max_reviews:
            response = requests.get(f"{url}&cursor={cursor}&filter=recent")
            if response.status_code != 200:
                print(f"Failed to fetch reviews: {response.status_code}")
                break

            data = response.json()
            if "reviews" not in data or len(data["reviews"]) == 0:
                print("No more reviews to fetch.")
                break

            reviews = data["reviews"]

            new_reviews = [
                review for review in reviews
                if review["review"] not in seen_reviews
            ]

            seen_reviews.update(review["review"] for review in new_reviews)

            if not new_reviews:
                print("No new reviews found. Ending fetch.")
                break

            for review in new_reviews:
                cleaned_review = self.clean_html_regex(review["review"])
                translated_review = self.translate_to_english(cleaned_review, translator)
                review["review_cleaned"] = translated_review

            all_reviews.extend(new_reviews)
            total_fetched += len(new_reviews)

            print(f"Fetched {len(new_reviews)} new reviews. Total: {total_fetched}")

            cursor = data.get("cursor", "*")
            time.sleep(delay)

            if total_fetched >= max_reviews:
                break

        reviews_df = pd.DataFrame([{
            "review": review["review_cleaned"],
            "voted_up": review["voted_up"]
        } for review in all_reviews])

        return reviews_df

    @staticmethod
    def clean_reviews(reviews_df, column="review"):
        reviews_df[column] = reviews_df[column].apply(SentimentAnalysisService.clean_html_regex)
        return reviews_df

    @staticmethod
    def analyze_sentiment(text):
        blob = TextBlob(text)
        return blob.sentiment.polarity

    @staticmethod
    def summarize_reviews_by_topic(reviews_df, lda_model, vectorizer):
        vectorized_reviews = vectorizer.transform(reviews_df['review'])

        if vectorized_reviews.shape[1] != lda_model.n_features_in_:
            raise ValueError("Feature count not same")

        topic_assignments = lda_model.transform(vectorized_reviews)
        reviews_df['topic'] = topic_assignments.argmax(axis=1)

        topic_summaries = {}
        for topic in range(lda_model.n_components):
            topic_reviews = reviews_df[reviews_df['topic'] == topic]
            topic_summary = topic_reviews['review'].str.cat(sep=' ')
            topic_summaries[topic] = topic_summary

        return topic_summaries

    def summarize_dominant_topic(self, topic_summaries, cleaned_reviews_df, n_top_phrases=3, ngram_range=2):
        dominant_topic = max(topic_summaries, key=lambda t: len(cleaned_reviews_df[cleaned_reviews_df['topic'] == t]))
        dominant_reviews = cleaned_reviews_df[cleaned_reviews_df['topic'] == dominant_topic]['review']

        combined_text = ' '.join(dominant_reviews)

        tokens = nltk.word_tokenize(combined_text.lower())
        n_grams = ngrams(tokens, ngram_range)

        phrase_counts = Counter(n_grams)
        top_phrases = phrase_counts.most_common(n_top_phrases)

        top_phrases_str = [' '.join(phrase) for phrase, _ in top_phrases]

        matching_sentences = dominant_reviews.str.split('.').explode().str.strip()

        matched_sentences = []
        for phrase in top_phrases_str:
            matches = matching_sentences[matching_sentences.str.contains(phrase, case=False, na=False)]
            matched_sentences.extend(matches.head(1))

        if len(matched_sentences) < n_top_phrases:
            additional_sentences = matching_sentences[~matching_sentences.isin(matched_sentences)].head(
                n_top_phrases - len(matched_sentences))
            matched_sentences.extend(additional_sentences)

        summary = matched_sentences[:3]

        sentiment_scores = dominant_reviews.apply(self.analyze_sentiment)

        positive_reviews = sentiment_scores[sentiment_scores > 0].count()
        negative_reviews = sentiment_scores[sentiment_scores < 0].count()
        total_reviews = sentiment_scores.count()

        positive_percentage = (positive_reviews / total_reviews) * 100
        negative_percentage = (negative_reviews / total_reviews) * 100

        if positive_percentage > negative_percentage:
            dominant_sentiment = True
            sentiment_percentage = positive_percentage
        else:
            dominant_sentiment = False
            sentiment_percentage = negative_percentage

        return dominant_topic, summary, dominant_sentiment, sentiment_percentage

    def analyze_app(self, app_id, num_per_page=1000):
        reviews_df = self.fetch_reviews(app_id, num_per_page)

        cleaned_reviews_df = self.clean_reviews(reviews_df)
        cleaned_reviews_df['sentiment'] = cleaned_reviews_df['review'].apply(self.analyze_sentiment)

        cleaned_reviews = cleaned_reviews_df['review'].tolist()
        vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
        X = vectorizer.fit_transform(cleaned_reviews)

        lda_model = LatentDirichletAllocation(n_components=5, random_state=42)
        lda_model.fit(X)

        feature_names = vectorizer.get_feature_names_out()
        topics = []
        for i, topic in enumerate(lda_model.components_):
            top_features_indices = topic.argsort()[:-6:-1]
            topics.append([feature_names[i] for i in top_features_indices])
            print(f"Topic {i}: {', '.join(topics[-1])}")

        cleaned_reviews_df = cleaned_reviews_df[['review', 'sentiment']]
        print(cleaned_reviews_df)

        X = cleaned_reviews_df['review']
        y = cleaned_reviews_df['sentiment'].apply(lambda x: 1 if x > 0 else 0)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        X_train_vec = vectorizer.transform(X_train)
        X_test_vec = vectorizer.transform(X_test)

        model = MultinomialNB()
        model.fit(X_train_vec, y_train)

        y_pred = model.predict(X_test_vec)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Accuracy: {accuracy}")
        print(classification_report(y_test, y_pred))

        topic_summaries = self.summarize_reviews_by_topic(cleaned_reviews_df, lda_model, vectorizer)
        dominant_topic, summary, overall_sentiment, sentiment_percentage = self.summarize_dominant_topic(topic_summaries, cleaned_reviews_df)

        return SentimentAnalyzeDto(
            summary=summary if summary else None,
            sentiment=overall_sentiment if overall_sentiment else None,
            percentage=f"{sentiment_percentage:.2f}%" if sentiment_percentage else None
        )