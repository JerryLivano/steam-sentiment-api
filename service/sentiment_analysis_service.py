import re
import time
import requests
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report
from textblob import TextBlob

class SentimentAnalysisService:
    # Clean unused characters
    def clean_html_regex(self, text):
        clean_text = re.sub(r'\[.*?\]', '', text)
        clean_text = re.sub(r'[\*\/*\\]', '', clean_text)
        clean_text = re.sub(r'\s+', ' ', clean_text)
        return clean_text.strip()

    # Fetch reviews
    def fetch_unique_reviews(self, app_id, max_reviews=1000, num_per_page=100, delay=1):
        url = f"https://store.steampowered.com/appreviews/{app_id}?json=1&num_per_page={num_per_page}"
        all_reviews = []
        seen_reviews = set()
        cursor = "*"
        total_fetched = 0

        while total_fetched < max_reviews:
            # Fetch data from the API
            response = requests.get(f"{url}&cursor={cursor}&filter=recent")  # Adding filter=recent
            if response.status_code != 200:
                print(f"Failed to fetch reviews: {response.status_code}")
                break

            data = response.json()
            if "reviews" not in data or len(data["reviews"]) == 0:
                print("No more reviews to fetch.")
                break

            reviews = data["reviews"]

            # Filter out duplicate reviews
            new_reviews = [
                review for review in reviews
                if review["review"] not in seen_reviews
            ]

            # Update the seen_reviews set
            seen_reviews.update(review["review"] for review in new_reviews)

            if not new_reviews:
                print("No new reviews found. Ending fetch.")
                break

            all_reviews.extend(new_reviews)
            total_fetched += len(new_reviews)

            print(f"Fetched {len(new_reviews)} new reviews. Total: {total_fetched}")

            # Update the cursor for the next request
            cursor = data.get("cursor", "*")

            # Delay between requests to avoid hitting rate limits
            time.sleep(delay)

        # Convert to DataFrame
        reviews_df = pd.DataFrame([{
            "review": review["review"],
            "voted_up": review["voted_up"]  # True for positive, False for negative
        } for review in all_reviews])

        return reviews_df

    # Function to clean reviews in a DataFrame
    def clean_reviews(self, reviews_df, column="review"):
        reviews_df[column] = reviews_df[column].apply(self.clean_html_regex)
        return reviews_df

    # Fungsi untuk analisis sentimen
    def analyze_sentiment(text):
        blob = TextBlob(text)
        return blob.sentiment.polarity

    def analyze_app(self, app_id = "578080", num_per_page = 1000):
        reviews_df = self.fetch_unique_reviews(app_id, num_per_page)

        # Clean the fetched reviews
        cleaned_reviews_df = self.clean_reviews(reviews_df)

        # Display summary of cleaned reviews
        cleaned_reviews_summary = cleaned_reviews_df["review"]
        print(cleaned_reviews_summary)

        # Bersihkan data dan buat vector term
        cleaned_reviews = cleaned_reviews_df['review'].tolist()
        vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
        x = vectorizer.fit_transform(cleaned_reviews)

        # Latent Dirichlet Allocation (LDA)
        lda_model = LatentDirichletAllocation(n_components=5, random_state=42)
        lda_topics = lda_model.fit_transform(x)

        # Mengambil topik-topik utama
        feature_names = vectorizer.get_feature_names_out()
        topics = []
        for i, topic in enumerate(lda_model.components_):
            top_features_indices = topic.argsort()[:-6:-1]  # 5 top features per topic
            topics.append([feature_names[i] for i in top_features_indices])
            print(f"Topic {i}: {', '.join(topics[-1])}")

        # Analisis sentimen untuk setiap review dalam aspek
        cleaned_reviews_df['sentiment'] = cleaned_reviews_df['review'].apply(self.analyze_sentiment)

        # Ringkasan analisis sentimen
        sentiment_summary = cleaned_reviews_df[['review', 'sentiment']]
        print(sentiment_summary)

        # Data bersih dengan sentimen
        cleaned_reviews_df = cleaned_reviews_df[['review', 'sentiment']]

        # Bagi data menjadi data latih dan data uji
        x = cleaned_reviews_df['review']
        y = cleaned_reviews_df['sentiment'].apply(lambda x: 1 if x > 0 else 0)  # 1 untuk positif, 0 untuk negatif
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

        # Representasi data dengan CountVectorizer
        vectorizer = CountVectorizer(max_features=5000)
        x_train_vec = vectorizer.fit_transform(x_train)
        x_test_vec = vectorizer.transform(x_test)

        # Pelatihan model Naive Bayes
        model = MultinomialNB()
        model.fit(x_train_vec, y_train)

        # Evaluasi model
        y_pred = model.predict(x_test_vec)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Accuracy: {accuracy}")
        print(classification_report(y_test, y_pred))