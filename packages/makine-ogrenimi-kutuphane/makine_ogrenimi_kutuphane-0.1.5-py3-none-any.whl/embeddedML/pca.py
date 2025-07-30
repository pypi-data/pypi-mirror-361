import numpy as np
class PCA:
    def __init__(self):
        self.eig_vals=None
        self.eig_vecs=None
        self.n_components = None
    def transform(self, X, n_components=2, conv_mode=1):
        self.n_components = n_components
        X_meaned = X - np.mean(X, axis=0)
        if conv_mode == 1:
            cov_mat = np.cov(X_meaned, rowvar=False)
        else:
            cov_mat = np.dot(X_meaned.T, X) / (len(X_meaned) - 1)
        self.eig_vals, self.eig_vecs = np.linalg.eigh(cov_mat)
        sorted_index = np.argsort(self.eig_vals)[::-1]
        sorted_eigvecs = self.eig_vecs[:, sorted_index]
        eigvec_subset = sorted_eigvecs[:, 0:n_components]
        X_reduced = np.dot(X_meaned, eigvec_subset)
        return X_reduced

    def calculate_explained_variance(self):
        sort_eigen_values = np.sort(self.eig_vals)[::-1]
        toplam = (np.sum(sort_eigen_values[:self.n_components]))
        return toplam / sum(self.eig_vals) * 100.0

    def select_components(self, X, variance_threshold=90):
        X_meaned = X - np.mean(X, axis=0)
        cov_mat = np.dot(X_meaned.T, X) / (len(X_meaned) - 1)
        self.eig_vals, self.eig_vecs = np.linalg.eigh(cov_mat)
        sort_eigen_values = np.sort(self.eig_vals)[::-1]
        total = np.sum(sort_eigen_values)
        value = np.cumsum(sort_eigen_values) / total * 100.0
        n_components = np.searchsorted(value, variance_threshold) + 1
        return n_components
    def transform_selecting_components(self, X, variance_threshold=90):
        X_meaned = X - np.mean(X, axis=0)
        cov_mat = np.dot(X_meaned.T, X) / (len(X_meaned) - 1)
        self.eig_vals, self.eig_vecs = np.linalg.eigh(cov_mat)
        sort_eigen_values = np.sort(self.eig_vals)[::-1]
        sorted_index = np.argsort(self.eig_vals)[::-1]
        total = np.sum(sort_eigen_values)
        value = np.cumsum(sort_eigen_values) / total * 100.0
        n_components = np.searchsorted(value, variance_threshold) + 1
        self.n_components = n_components
        sorted_eigvecs = self.eig_vecs[:, sorted_index]
        eigvec_subset = sorted_eigvecs[:, 0:n_components]
        X_reduced = np.dot(X_meaned, eigvec_subset)
        return X_reduced


