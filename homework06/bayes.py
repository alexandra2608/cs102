from collections import Counter
from math import log


class NaiveBayesClassifier:
    def __init__(self, alpha):
        self.alpha = alpha

    def fit(self, X, y):
        """Fit Naive Bayes classifier according to X, y."""
        self.words_dict = Counter()
        self.words_numbers = Counter()
        self.labels_words_numbers = Counter()

        for item, label in zip(X, y):
            for word in item.split():
                self.words_dict[word, label] += 1
                self.words_numbers[word] += 1
                self.labels_words_numbers[label] += 1

        self.words_dict = dict(self.words_dict)
        self.words_numbers = dict(self.words_numbers)
        self.labels_numbers = dict(Counter(y))

        self.label_prob = dict()
        for label in self.labels_numbers:
            self.label_prob[label] = self.labels_numbers[label] / len(y)

        self.word_prob = dict()
        for word in self.words_numbers:
            self.word_prob[word] = dict()
            for label in self.labels_numbers:
                self.word_prob[word][label] = (self.words_dict.get((word, label), 0) + self.alpha) / (
                    self.labels_words_numbers[label] + self.alpha * len(self.words_numbers)
                )

    def predict(self, X):
        """Perform classification on an array of test vectors X."""
        predictions = []
        for item in X:
            max_prob = float("-inf")
            label_to_give = ""

            for label in self.label_prob:
                this_prob = log(self.label_prob[label])
                # this_prob += log(1 / len(self.labels_numbers))
                for word in item.split():
                    if word in self.word_prob and label in self.word_prob[word]:
                        this_prob += log(self.word_prob[word][label])

                if this_prob > max_prob:
                    max_prob = this_prob
                    label_to_give = label
            predictions.append(label_to_give)

        return predictions

    def score(self, X_test, y_test):
        """Returns the mean accuracy on the given test data and labels."""
        predictions = self.predict(X_test)
        correct = 0

        for i in range(len(predictions)):
            if predictions[i] == y_test[i]:
                correct += 1
        return correct / len(y_test)
