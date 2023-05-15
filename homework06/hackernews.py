import pickle
import string

import nltk  # type: ignore
from bayes import NaiveBayesClassifier
from bottle import error, redirect, request, route, run, template  # type: ignore
from db import News, session
from scraputils import get_news


@route("/")
@route("/news")
def news_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template("news_template", rows=rows)


@route("/add_label/")
def add_label():
    s = session()
    line = s.query(News).filter(News.id == request.query["id"]).first()
    line.label = request.query["label"]
    s.commit()
    if __name__ == "__main__":
        redirect("/news")


def clean(s):
    """Preparing text data"""
    translator = str.maketrans("", "", string.punctuation)
    return s.translate(translator)


@route("/update")
def update_news():
    """Adding more news"""
    s = session()
    newz = get_news("https://news.ycombinator.com/newest", n_pages=3)
    for example in newz:
        if not s.query(News).filter(News.author == example["author"], News.title == example["title"]).first():
            new = News(
                title=example["title"],
                author=example["author"],
                url=example["url"],
                comments=example["comments"],
                points=example["points"],
            )
            s.add(new)
            s.commit()
    if __name__ == "__main__":
        redirect("/news")


@route("/classify")
def classify_news():
    """Classifying news"""
    s = session()
    news_cl = s.query(News).filter(News.label != None).all()
    x_train = [row.title for row in news_cl]
    y_train = [row.label for row in news_cl]
    model = NaiveBayesClassifier(1)
    x_train = [clean(x).lower() for x in x_train]
    model.fit(x_train, y_train)
    news_not_cl = s.query(News).filter(News.label == None).all()

    first_priority, second_priority, third_priority = [], [], []
    for row in news_not_cl:
        article = [row.title]
        article = [clean(t).lower() for t in article]
        prediction = model.predict(article)
        s.query(News).get(row.id).label = prediction[0]
        s.commit()
        match prediction[0]:
            case "good":
                first_priority.append(row)
            case "maybe":
                second_priority.append(row)
            case "never":
                third_priority.append(row)

    recs = first_priority + second_priority + third_priority
    return recs


@route("/recommendations")
def recommendations():
    """Recommendations from good to never"""
    s = session()
    recs = classify_news()
    news = s.query(News).filter(News.label != None).all()
    first_priority, second_priority, third_priority = [], [], []
    for piece in news:
        match piece.label:
            case "good":
                first_priority.append(piece)
            case "maybe":
                second_priority.append(piece)
            case "never":
                third_priority.append(piece)
    res = first_priority + second_priority + third_priority
    return template("news_recommendations", rows=res)
