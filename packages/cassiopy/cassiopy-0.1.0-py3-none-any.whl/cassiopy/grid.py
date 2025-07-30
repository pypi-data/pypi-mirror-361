import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import inspect
import os
import h5py
from cassiopy.mixture import SkewTMixture, SkewTUniformMixture


import sys
sys.path.append('../../')

class Grid:
    """
    A class representing a grid search over SkewT mixture models with varying parameters.

    Parameters
    ==========
    - n_cluster (int or list): Number of clusters to test.
    - n_ori (int or list): Number of orientations to test.
    - c1 (float or list): List of c1 regularization parameters to test.
    - n_fits (int): Number of fits to perform for each configuration.
    - max_iter (int): Maximum number of iterations for fitting.
    - metric (str): Evaluation metric. Options: 'BIC', 'AIC', 'KL', 'IUS', 'chi2', 'L2', 'HARTIGAN'.
    - model (str): Mixture model class name ('SkewTUniformMixture', 'SkewTMixture').

    Methods
    ========
    - fit(x): Fits models on data `x` across the parameter grid.
    """

    def __init__(self, n_cluster=5, n_fits=2, max_iter=1000, model=None):
        # Convert scalars to lists
        self.n_cluster = n_cluster if isinstance(n_cluster, (list, tuple)) else [n_cluster]

        self.n_fits = n_fits+1
        self.max_iter = max_iter


        # Load model
        if model is None:
            raise ValueError("Model must be specified: 'SkewTUniformMixture', or 'SkewTMixture'.")
        elif model == 'SkewTUniformMixture':
            from cassiopy.mixture import SkewTUniformMixture
            self.mixture_class = SkewTUniformMixture
        elif model == 'SkewTMixture':
            from cassiopy.mixture import SkewTMixture
            self.mixture_class = SkewTMixture
        else:
            raise ValueError(f"Unsupported model: {model}")

        self.models = []
        self.metric = None

    def fit(self, x, verbose=0):
        """
        Fit the mixture model to the data `x` across the parameter grid.
        
        Parameters
        ==========
        - x (array-like): Input data.
        
        Returns
        =======
        - self
        """

        for i, k in enumerate(self.n_cluster):
            for f in range(self.n_fits):
                model = self.mixture_class(n_cluster=k)
                model.fit(X=x, max_iter=self.max_iter, verbose=verbose)
                model.save(f"Model_{k}_cluster_fit{f}.h5")
                print(f"[✓] Fitted: clusters={k}, fit={f}")

        return self
    
    def hartigan_scores(self, x):
        """
        Calcule la statistique de Hartigan entre k et k+1 clusters.
        
        Parameters
        ==========
        - x (array-like): Données d'entrée (nécessaire pour connaître n).
        
        Returns
        =======
        - np.array: Tableau des scores Hartigan.
        """
        n = x.shape[0]
        scores = []

        for i in range(len(self.n_cluster) - 1):
            Wk = np.min(self.metric[i])  # score pour k clusters
            Wk1 = np.min(self.metric[i + 1])  # score pour k+1 clusters
            H = ((Wk / Wk1) - 1) * (n - self.n_cluster[i + 1] - 1)
            scores.append(H)

        return np.array(scores)


    def best_model(self, x=None, threshold=10, metric='Hartigan'):
        """
        Sélectionne et charge le meilleur modèle selon la métrique choisie.

        Parameters
        ==========
        - x (array-like, optional): Requis uniquement si la métrique est 'HARTIGAN'.
        - threshold (float): Seuil de décision pour la statistique de Hartigan.

        Returns
        =======
        - best_model: Le modèle entraîné correspondant à la meilleure configuration.
        """
        self.metric_name = metric.upper()
        n_k = len(self.n_cluster)

        self.metric = np.zeros((n_k, self.n_fits))
        if self.metric_name in ['BIC', 'AIC', 'KL', 'chi2', 'L2', 'IUS', 'HARTIGAN']:
            for i, k in enumerate(self.n_cluster):
                for f in range(self.n_fits):
                    model = self.mixture_class(n_cluster=k)
                    model.load(f"Models_folder/Model_{k}_cluster_fit{f}.h5")
                    score_method = getattr(model, self.metric_name)
                    score = score_method(X=x)
                    self.metric[i, f] = score[0] if isinstance(score, tuple) else score
        else:
            raise ValueError(f"Unknown metric '{self.metric_name}'")


        metric_mode = 'min' if self.metric_name in ['BIC', 'AIC', 'KL', 'chi2', 'L2'] else 'max'

        if self.metric_name == 'HARTIGAN':
            if x is None:
                raise ValueError("Données requises pour le calcul de la statistique de Hartigan.")
            hs = self.hartigan_scores(x)
            # Trouver le plus petit k tel que Hartigan > threshold
            for i, h in enumerate(hs):
                if h > threshold:
                    k = i
                    break
            else:
                k = np.argmax(hs)  # choisir le meilleur score si aucun ne dépasse le seuil
        else:
            if metric_mode == 'min':
                k, f = np.unravel_index(np.argmin(self.metric), self.metric.shape)
            else:
                k, f = np.unravel_index(np.argmax(self.metric), self.metric.shape)

        n_cluster = self.n_cluster[k]

        model = self.mixture_class(n_cluster=n_cluster)

        # Chemin du modèle sauvegardé
        filename = f"Models_folder/Model_{n_cluster}_cluster_fit{f}.h5"
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Modèle non trouvé: {filename}")

        model.load(filename)
        return model
    
    def best_nbre_cluster(self, x=None, threshold=10, metric='Hartigan'):
        """
        Retourne le nombre de clusters du meilleur modèle selon la métrique choisie.

        Parameters
        ==========
        - x (array-like, optional): Requis pour la méthode Hartigan.
        - threshold (float): Seuil Hartigan si utilisé.

        Returns
        =======
        - int: Nombre optimal de clusters.
        """
        
        self.metric_name = metric.upper()
        n_k = len(self.n_cluster)

        self.metric = np.zeros((n_k, self.n_fits))
        if self.metric_name in ['BIC', 'AIC', 'KL', 'chi2', 'L2', 'IUS', 'HARTIGAN']:
            for i, k in enumerate(self.n_cluster):
                for f in range(self.n_fits, ):
                    model = self.mixture_class(n_cluster=k)
                    model.load(f"Models_folder/Model_{k}_cluster_fit{f}.h5")
                    score_method = getattr(model, self.metric_name)
                    score = score_method(X=x)
                    self.metric[i, f] = score[0] if isinstance(score, tuple) else score

        else:
            raise ValueError(f"Unknown metric '{self.metric_name}'")

        if self.metric_name == 'HARTIGAN':
            if x is None:
                raise ValueError("Les données x sont requises pour la métrique 'HARTIGAN'.")
            hs = self.hartigan_scores(x)
            for i, h in enumerate(hs):
                if h > threshold:
                    k = i
                    break
            else:
                k = np.argmax(hs)
        else:
            metric_mode = 'min' if self.metric_name in ['BIC', 'AIC', 'KL', 'chi2', 'L2'] else 'max'
            idx_fn = np.argmin if metric_mode == 'min' else np.argmax
            k, _ = np.unravel_index(idx_fn(self.metric), self.metric.shape)

        return self.n_cluster[k]