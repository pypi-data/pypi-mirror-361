import numpy as np

class NaiveBayesFast:
    def __init__(self):
        self.summaries = {}

    def mean(self, array):
        return np.mean(array)

    def stdev(self, array):
        return np.std(array, ddof=1)  # sample std

    def gaussian_probability(self, x, mean, stdev):
        if stdev == 0:
            return 1.0
        exponent = np.exp(-((x - mean) ** 2) / (2 * stdev ** 2))
        return exponent / (stdev * np.sqrt(2 * np.pi))

    def separate_by_class(self, X, y):
        separated = {}
        for xi, yi in zip(X, y):
            if yi not in separated:
                separated[yi] = []
            separated[yi].append(xi)
        for label in separated:
            separated[label] = np.array(separated[label])
        return separated

    def train(self, X, y):
        separated = self.separate_by_class(X, y)
        summaries = {}
        for class_value, rows in separated.items():
            means = np.mean(rows, axis=0)
            stdevs = np.std(rows, axis=0, ddof=1)
            summaries[class_value] = list(zip(means, stdevs))
        self.summaries = summaries

    def calculate_class_probabilities(self, input_vector):
        probabilities = {}
        for class_value, class_summaries in self.summaries.items():
            probs = [self.gaussian_probability(x, mean, stdev)
                     for x, (mean, stdev) in zip(input_vector, class_summaries)]
            probabilities[class_value] = np.prod(probs)
        return probabilities

    def predict(self, X):
        predictions = []
        for input_vector in X:
            probabilities = self.calculate_class_probabilities(input_vector)
            best_label = max(probabilities, key=probabilities.get)
            predictions.append(best_label)
        return np.array(predictions)