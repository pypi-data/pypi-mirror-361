import numpy as np
import os
import scipy
from cassiopy.stats import SkewT
import pandas as pd
from scipy.special import digamma, loggamma
from scipy.optimize import minimize_scalar
from scipy.stats import skewnorm, norm, gamma, t 



class SkewTMixture:
    """
    SkewTMixture
    ============
    A mixture model for clustering using the skewed Student's t-distribution.

    Parameters
    ==========
    n_cluster : int
        Number of clusters.
    init_method : str, default='gmm'
        Initialization method. Options: 'gmm', 'kmeans', 'params'.
    parametre : dict, optional
        Dictionary of initial parameters if init_method='params'.
    n_init_gmm : int, default=6
        Number of initializations for GMM.

    Attributes
    =========
    mean : ndarray
        Cluster means.
    sigma : ndarray
        Cluster standard deviations.
    dl : ndarray
        Degrees of freedom for each cluster.
    lamb : ndarray
        Skewness parameters for each cluster.
    alpha : ndarray
        Cluster weights.
    tik : ndarray
        Posterior probabilities.
    logli : list
        Log-likelihood values during training.


    Notes
    =====

    For more information, refer to the documentation :ref:`doc.mixture.SkewTMixture`

    Examples
    ========
    >>> import numpy as np
    >>> from cassiopy.mixture import SkewTMixture
    >>> X = np.array([[5, 3], [5, 7], [5, 1], [20, 3], [20, 7], [20, 1]])
    >>> model = SkewTMixture(n_cluster=2, init_method='kmeans')
    >>> model.fit(X, max_iter=100, tol=1e-4)
    >>> model.mean
    array([[ 5.        ,  1.40735413],
       [20.00000058,  0.66644041]])
    >>> model.predict_proba(np.array([[0, 0], [22, 5]]))
    array([[0.5, 0.5],
       [0.5, 0.5]])
    >>> model.save('model.h5')
    >>> model.load('Models_folder/model.h5')
    >>> model.predict_cluster(np.array([[0, 0], [22, 5]]))
    array([0., 0.])
    """

    def __init__(self, n_cluster:int, init_method='gmm', parametre=None, n_init_gmm=6):
        self.n_cluster = n_cluster
        self.init_method = init_method

        if self.init_method == "params":
            self.params = parametre

        if self.init_method == "gmm":
            self.n_init_gmm = n_init_gmm

    def initialisation_random(self, X):
        """
        Initialize the parameters randomly for the SkewMM algorithm.

        Parameters
        ==========
        X : array-like of shape (n_samples, n_features)
            Input data matrix.

        Returns
        =======
        w : ndarray of shape (n_clusters,)
            Cluster weights.

        mu : ndarray of shape (n_clusters, n_features)
            Cluster means.

        s : ndarray of shape (n_clusters, n_features)
            Cluster standard deviations.

        nu : ndarray of shape (n_clusters, n_features)
            Degrees of freedom for each cluster.

        la : ndarray of shape (n_clusters, n_features)
            Skewness parameters for each cluster.
        
        """
        w = np.random.uniform(0.1, 1.0, size=self.n_cluster)
        w /= np.sum(w)

        mu = np.random.uniform(np.min(X, axis=0), np.max(X, axis=0), size=(self.n_cluster, X.shape[1]))
        s = np.random.uniform(0.1, 1.0, size=(self.n_cluster, X.shape[1]))
        nu = np.random.uniform(4., 10., size=(self.n_cluster, X.shape[1]))
        la = np.random.uniform(-2., 2., size=(self.n_cluster, X.shape[1]))

        return w, mu, s, nu, la

    def initialisation_gmm(self, X):
        """
        Initialize the parameters for the Gaussian Mixture Model (GMM).

        Parameters
        ==========
        X : array-like of shape (n_samples, n_features)
            Input data matrix.

        Returns
        =======
        w : ndarray of shape (n_clusters,)
            Cluster weights.

        mu : ndarray of shape (n_clusters, n_features)
            Cluster means.

        s : ndarray of shape (n_clusters, n_features)
            Cluster standard deviations.

        nu : ndarray of shape (n_clusters, n_features)
            Degrees of freedom for each cluster.

        la : ndarray of shape (n_clusters, n_features)
            Skewness parameters for each cluster.
        
        """
        from sklearn.mixture import GaussianMixture

        gmm = GaussianMixture(n_components=self.n_cluster, covariance_type='diag').fit(X)
        mu = gmm.means_
        s = np.sqrt(gmm.covariances_)
        w = gmm.weights_
        la = np.random.uniform(low=1e-6, high=1e-5, size=(self.n_cluster, X.shape[1]))
        nu = np.random.uniform(0, 10, size=(self.n_cluster, X.shape[1]))
        return w, mu, s, nu, la
    
    def initialisation_kmeans(self, X):
        """
        Initializes the parameters for the SkewMM algorithm using the K-means initialization method.

        Parameters
        ==========
        X : array-like of shape (n_samples, n_features)
            The input data matrix.

        default_n_init : int, default='auto'
            The number of times the K-means algorithm will be run with different centroid seeds. Default is 'auto'.

        Returns
        =======
        dict : dict
            A dictionary containing the initialized parameters:

        w : ndarray of shape (n_clusters,)
            Cluster weights.

        mu : ndarray of shape (n_clusters, n_features)
            Cluster means.
        
        s : ndarray of shape (n_clusters, n_features)
            Cluster standard deviations.

        nu : ndarray of shape (n_clusters, n_features)
            Degrees of freedom for each cluster.
            
        la : ndarray of shape (n_clusters, n_features)
            Skewness parameters for each cluster.
        """
        from sklearn.cluster import KMeans

        kmeans = KMeans(n_clusters=self.n_cluster, n_init=20).fit(X)
        mu = kmeans.cluster_centers_
        s = np.ones((self.n_cluster, X.shape[1]))
        w = np.bincount(kmeans.labels_) / len(kmeans.labels_)
        la = np.random.uniform(low=1e-6, high=1e-5, size=(self.n_cluster, X.shape[1]))
        nu = np.random.uniform(0, 10, size=(self.n_cluster, X.shape[1]))
        return w, mu, s, nu, la

    

    def logt_expr(self, eta2, nu):
        """
        Compute the logarithm of the t-distribution expression.
        Parameters
        ==========
        eta2 : ndarray
            Squared standardized residuals.
        nu : ndarray
            Degrees of freedom.

        Returns
        =======
        logt_val : ndarray
            Logarithm of the t-distribution expression.
        """
        return loggamma((nu + 1)/2) - loggamma(nu/2) - 0.5 * np.log(nu * np.pi) - ((nu + 1)/2) * np.log(1 + eta2 / nu)

    def ST(self, X, w, mu, s, nu, la): 
        """
        Compute the posterior probabilities for the SkewT mixture model.

        Parameters
        ==========
        X : ndarray
            Input data.

        w : ndarray
            Cluster weights.

        mu : ndarray
            Cluster means.

        s : ndarray
            Cluster standard deviations.

        nu : ndarray
            Degrees of freedom for each cluster.

        la : ndarray
            Skewness parameters for each cluster.

        Returns
        =======
        Z : ndarray
            Posterior probabilities for each cluster.
        """
        Skew = np.ones((len(w), X.shape[0])) 
        
        if X.ndim == 1:
            eta = (X[None, :] - mu[:, None]) / s[:, None]
            logt_val = self.logt_expr(eta**2, nu[:, None])

            lau = la[:, None] * eta
            t0 = (nu[:, None] + 1) / (nu[:, None]+ eta**2)
            c0 = lau * np.sqrt(t0)
            Tc0 = t.cdf(c0, df=nu[:, None] + 1)
            Skew = w[:, None] * 2 * np.exp(logt_val) * Tc0 / s[:, None]
            
        else:
            Skew *=  w[:, None]

            for j in range(X.shape[1]):

                eta = (X[:, j][None, :] - mu[:, j][:, None]) / s[:, j][:, None]
                logt_val = self.logt_expr(eta**2, nu[:, j][:, None])

                lau = la[:, j][:, None] * eta
                t0 = (nu[:, j][:, None] + 1) / (nu[:, j][:, None]+ eta**2)
                c0 = lau * np.sqrt(t0)

                Tc0 = t.cdf(c0, df=nu[:, j][:, None] + 1)

                Skew *= 2 * np.exp(logt_val) * Tc0 / s[:, j][:, None]

        return Skew


    def LL(self, Z):
        """
        Compute the log-likelihood of the model.

        Parameters
        ==========

        Z : ndarray
            Posterior probabilities for each cluster.

        Returns
        =======
        logli_new : float
            Log-likelihood of the model.
        """
        ind_den = np.sum(Z, axis=0)
        logli_new = np.sum(np.log(ind_den))
        return logli_new

    def fit(self, X, tol=1e-6, max_iter=200, verbose=0):
        """
        Fit the SkewT mixture model to the data.
        
        Parameters
        ==========
        X : array-like, shape (n_samples, n_features)
            The input data.

        tol : float, default=1e-6
            Tolerance for convergence.

        max_iter : int, default=200
            Maximum number of iterations for the EM algorithm.

        """
        if self.init_method == 'gmm':
            best_params = None
            best_LL = -np.inf
            params_to_test = [
                    self.initialisation_gmm(X) for _ in range(self.n_init_gmm)
                ]
            
            for params in params_to_test:
                w, mu, s, nu, la = params
                Z = self.ST(X, w, mu, s, nu, la)
                LL = self.LL(Z)
                if LL > best_LL:
                    best_LL = LL
                    best_params = params
            w, mu, s, nu, la = best_params
        
        elif self.init_method == 'random':
            w, mu, s, nu, la = self.initialisation_random(X)
            
        elif self.init_method == 'kmeans':
            w, mu, s, nu, la = self.initialisation_kmeans(X)

        elif self.init_method == 'parametre':
            w = self.params['alpha']
            mu = self.params['mu']
            s = self.params['sig']
            la = self.params['lamb']
            nu = self.params['nu']

        else : 
            raise ValueError(f"Error: The initialization method {self.init_method} is not recognized, please choose from 'parametre', 'kmeans', or 'gmm' ")

        if X.ndim == 1:
            n, dim = len(X), 1
        else:
            n, dim = X.shape[0], X.shape[1]

        g = len(w) if isinstance(w, (list, np.ndarray)) else 1
        if g == 1:
            w = np.array([w])
            mu = np.array([mu])
            s = np.array([s])
            la = np.array([la])
            nu = np.array([nu])


        iter = 0

        eta = (X[None, :] - mu[:, None]) / s[:, None]
        eta2 = eta**2
        lau = la[:, None] * eta
        t0 = (nu[:, None] + 1) / (nu[:, None] + eta2)
        c0 = lau * np.sqrt(t0)
        Tc0 = t.cdf(c0, df=nu[:, None] + 1)
        Z = self.ST(X, w, mu, s, nu, la) # ST
        ind_den = np.sum(Z, axis=0)
        logli_old = self.LL(Z)
        self.logli = [self.LL(Z)]

        while True:
            # E-step
            if verbose==1:
                print(f'iteration: {iter}/{max_iter}')
            iter += 1
            ind_den = np.sum(Z, axis=0)

            Z /= ind_den
            c2 = la[:, None] * eta * np.sqrt((nu[:, None] + 3) / (nu[:, None] + eta2))
            Tc2 = t.cdf(c2, df=nu[:, None] + 3)
            tau = t0 * Tc2 / Tc0
            de = la / np.sqrt(1 + la**2)
            al = s * de
            hs1 = (lau * tau + t.pdf(c0, df=nu[:, None] + 1) / Tc0 * np.sqrt(t0)) * np.sqrt(1 - de[:, None]**2)
            hs2 = 1 - de[:, None]**2 + de[:, None] * eta * hs1


            # M-step
            ni= np.sum(Z, axis=1)
            w = ni / n
        
            mu = np.sum(Z[:, :, None] * (tau * X - (al[:, None] * hs1)), axis=1) / np.sum(Z[:, :, None] * tau, axis=1)
            cent = (X[None, :] - mu[:, None])
            Szs2 = np.sum(Z[:, :, None] * hs2, axis=1)
            al = np.sum(Z[:, :, None] * hs1 * cent, axis=1) / Szs2


            ka2 = np.sum(Z[:, :, None] * (tau * cent**2 - 2 * al[:, None] * hs1 * cent + (al**2)[:, None] * hs2), axis=1) / ni[:, None]
            s = np.sqrt(ka2 + al**2)
            de = al / s
            la = de / np.sqrt(1 - de**2)


            for i in range(g):
                if dim == 1:
                    def CML_nu(v):
                        cdf_vals = t.cdf(la[i] * np.sqrt((v + 1) / (v + eta2[i, :])), df=v + 1)
                        log_t = self.logt_expr(eta2[i, :], v)
                        return -np.sum(Z[i, :] * (log_t + np.log(cdf_vals)))
                    res = minimize_scalar(CML_nu, bounds=(1e-6, 100), method='bounded')
                    nu[i] = res.x
                else:
                    for j in range(dim):
                        def CML_nu(v):
                            cdf_vals = t.cdf(la[i, j] * np.sqrt((v + 1) / (v + eta2[i, :, j])), df=v + 1)
                            log_t = self.logt_expr(eta2[i, :, j], v)
                            return -np.sum(Z[i, :] * (log_t + np.log(cdf_vals)))
                        res = minimize_scalar(CML_nu, bounds=(1e-6, 100), method='bounded')
                        nu[i, j] = res.x


            eta = (X[None, :] - mu[:, None]) / s[:, None]
            eta2 = eta**2
            lau = la[:, None] * eta
            t0 = (nu[:, None] + 1) / (nu[:, None] + eta2)
            c0 = lau * np.sqrt(t0)
            Tc0 = t.cdf(c0, df=nu[:, None] + 1)
            Z = self.ST(X, w, mu, s, nu, la) # ST

            
            logli_new = self.LL(Z)

            diff = logli_new - logli_old
            if diff < tol or iter >= max_iter:
                print('tolérance atteinte')
                break

            if logli_new < logli_old:
                print('logli_new', logli_new)
                print('logli_old', logli_old)
                print('diminution du logli')
                break

            if iter == max_iter:
                print('nombre d iterations atteint')
                break
            
            logli_old = logli_new
            self.logli.append(logli_new)


        self.tik = Z/ ind_den

        self.mean = mu
        self.sigma = s
        self.dl = nu
        self.lamb = la
        self.alpha = w



        return self
    

    def predict_proba(self, X):
        """
        Predict the posterior probabilities for the data.

        Parameters
        ==========
        X : array-like, shape (n_samples, n_features)
            The input data.

        Returns
        =======
        proba : ndarray, shape (n_samples, n_clusters)
            The posterior probabilities for each cluster.
        """
        # Implementation of the predict_proba method
        Z = self.ST(X, self.alpha, self.mean, self.sigma, self.dl, self.lamb)
        ind_den = np.sum(Z, axis=0)
        proba = Z / ind_den
        return proba
    
    def predict(self, X):
        """
        Predict the cluster labels for the data.

        Parameters
        ==========
        - X (array-like): The input data.

        Returns
        =======
        - labels (array-like): The predicted cluster labels.
        """
        # Implementation of the predict method
        proba = self.predict_proba(X)
        labels=np.array([])
        for i in range(proba.shape[1]):
            labels = np.append(labels, np.argmax(proba[:, i]))
        return labels    
        
    def ARI(self, y_true, y_pred):
        """
        Compute the ARI .

        Parameters
        ==========
        - y (array-like): The true labels.

        Returns
        =======
        - ari (float): The Adjusted Rand Index (ARI) score.
        """
        from sklearn.metrics import adjusted_rand_score
        ari = adjusted_rand_score(y_true, y_pred)

        return ari

    def confusion_matrix(self, y_true, y_pred):
        """
        Calculate the confusion matrix.

        Parameters
        ==========
        y_true : array-like
            The true labels.

        y_pred : array-like, default=None
            The predicted labels.

        Returns
        =======
        matrix : array-like
            The confusion matrix. The last cluster correspond to the uniform cluster.
        """

        if y_true is None:
            raise ValueError("Error: The true labels are missing, please provide them.")

        y_true = y_true.astype(int)


        y_pred = np.array(y_pred).astype(int)

        # Obtenez les classes uniques
        classes = np.unique(np.concatenate((y_true, y_pred)))

        # Créez une matrice de confusion initialisée à zéro
        matrix = np.zeros((self.n_cluster, self.n_cluster), dtype=int)

        # Utilisez np.searchsorted pour obtenir les indices des classes
        true_indices = np.searchsorted(classes, y_true)
        pred_indices = np.searchsorted(classes, y_pred)

        # Mettez à jour la matrice de confusion en comptant les occurrences
        for true_idx, pred_idx in zip(true_indices, pred_indices):
            matrix[true_idx, pred_idx] += 1

        return matrix
    
    def BIC(self, X):
        """
        Calculate the Bayesian Information Criterion (BIC) for the model.

        Parameters
        ==========
        - X (array-like): The input data.

        Returns
        =======
        - bic (float): The BIC value.
        """
        # Implementation of the BIC method
        n = X.shape[0]
        LL = self.logli[-1]

        m = 4 * self.n_cluster
        bic = -2 * LL + np.log(n) * m

        return bic
    
    def AIC(self, X, penalty_weight=0.1):
        from collections import Counter
        # Implementation of the BIC method
        y_pred = self.predict(X)
        n = X.shape[0]
        LL = self.logli[-1]

        m = 4 * self.n_cluster
        aic = -2 * LL + 2* m

        cluster_sizes = Counter(y_pred)
        penalty = sum(1 for size in cluster_sizes.values() if size < 5)
        return aic * (1 - penalty_weight * penalty)

    def IUS(self, X, bins=3):
        """
        Calcule l'entropie de Shannon pour des données multidimensionnelles
        en utilisant une estimation par histogramme.

        Paramètres :
        - data : ndarray de forme (n_samples, n_features)
        - bins : nombre de divisions par dimension (ou liste)

        Retourne :
        - entropie de Shannon (en bits)
        """
        probabilites= self.tik[:,:]
        y_pred = self.predict(X)

        tirage_bernoulli = np.random.binomial(1, probabilites)

        label_bernouilli = np.zeros(X.shape[0])

        for i in range(X.shape[0]):
            if tirage_bernoulli[i]==1:
                label_bernouilli[i]= self.n_cluster
            else:
                label_bernouilli[i]=y_pred[i]

        data = X[:, :][label_bernouilli == self.n_cluster]

        # Histogramme multidimensionnel
        hist, edges = np.histogramdd(data, bins=bins)

        # Probabilités (normalisation)
        prob = hist / np.sum(hist)

        # Entropie (en bits)
        prob_nonzero = prob[prob > 0]
        H = -np.sum(prob_nonzero * np.log2(prob_nonzero))

        # Entropie maximale = log2(N) où N est le nombre total de cases non nulles
        N = np.sum(hist)
        H_max = np.log2(N) if N > 0 else 1e-12  # pour éviter la division par zéro

        # Indice d’uniformité
        iuS = H / H_max if H_max > 0 else 0

        return iuS
    
    def KL(self, X, bins=3):
        from scipy.special import rel_entr
        probabilites= self.tik[: ,:]
        y_pred = self.predict(X)

        tirage_bernoulli = np.random.binomial(1, probabilites)

        label_bernouilli = np.zeros(X.shape[0])

        for i in range(X.shape[0]):
            if tirage_bernoulli[i]==1:
                label_bernouilli[i]= self.n_cluster
            else:
                label_bernouilli[i]=y_pred[i]

        data = X[:, :][label_bernouilli == self.n_cluster]

        hist, _ = np.histogramdd(data, bins=bins)
        prob = hist / np.sum(hist)
        
        uniform_prob = 1 / np.prod(hist.shape)
        kl_div = np.sum(rel_entr(prob, uniform_prob))
        
        return kl_div
    
    def L2(self, X, bins=10, penalty_weight=0.1):
        from scipy.spatial.distance import cdist
        from collections import Counter
        probabilites= self.tik[:,:]
        y_pred = self.predict(X)

        tirage_bernoulli = np.random.binomial(1, probabilites)

        label_bernouilli = np.zeros(X.shape[0])

        for i in range(X.shape[0]):
            if tirage_bernoulli[i]==1:
                label_bernouilli[i]= self.n_cluster
            else:
                label_bernouilli[i]=y_pred[i]

        
        data = X[:, :][label_bernouilli == self.n_cluster]

        hist, _ = np.histogramdd(data, bins=bins)
        prob = hist / np.sum(hist)
        
        uniform_prob = 1 / np.prod(hist.shape)
        l2_distance = np.sqrt(np.sum((prob - uniform_prob) ** 2))

        cluster_sizes = Counter(y_pred)
        penalty = sum(1 for size in cluster_sizes.values() if size < 5)
        return l2_distance * (1 - penalty_weight * penalty)
    

    def chi2(self, X, bins=3):
        from scipy.stats import chisquare
        probabilites= self.tik[:,:]
        y_pred = self.predict(X)

        tirage_bernoulli = np.random.binomial(1, probabilites)

        label_bernouilli = np.zeros(X.shape[0])

        for i in range(X.shape[0]):
            if tirage_bernoulli[i]==1:
                label_bernouilli[i]= self.n_cluster
            else:
                label_bernouilli[i]=y_pred[i]

        data = X[:, :][label_bernouilli == self.n_cluster]
        hist, _ = np.histogramdd(data, bins=bins)
        observed = hist.flatten()
        expected = np.full_like(observed, np.mean(observed))
        chi2_stat, p_value = chisquare(f_obs=observed, f_exp=expected)
        return chi2_stat, p_value 

    def HARTIGAN(self, X):
        W = 0
        y_pred = self.predict(X)

        for cluster_id in np.unique(y_pred):
            cluster_points = X[y_pred == cluster_id]
            if len(cluster_points) == 0:
                continue  # éviter les clusters vides
            center = cluster_points.mean(axis=0)
            distances = np.linalg.norm(cluster_points - center, axis=1)
            W += np.sum(distances ** 2)
        return W
   

    def save(self, filename: str):
        """
        Save the model to a file.

        Parameters
        ==========
        filename : str
            The name of the file.
        """
        import h5py

        if not filename.endswith(".h5"):
            filename = f"{filename}.h5"

        if not filename:
            raise ValueError(
                "Error: The filename is empty, please provide a valid filename."
            )

        if not os.path.exists("Models_folder"):
            os.makedirs("Models_folder")

        with h5py.File(f"Models_folder/{filename}", "w") as f:
            f.create_dataset("mean", data=self.mean)
            f.create_dataset("sigma", data=self.sigma)
            f.create_dataset("dl", data=self.dl)
            f.create_dataset("lamb", data=self.lamb)
            f.create_dataset("alpha", data=self.alpha)
            f.create_dataset("tik", data=self.tik)
            f.create_dataset("E_log_likelihood", data=self.logli)

    def load(self, filename: str):
        """
        Load matrices from a given file.

        Parameters
        ==========
        filename : str
            The path to the file containing the matrices.
        """
        import h5py

        with h5py.File(filename, "r") as f:
            self.mean = f["mean"][:]
            self.sigma = f["sigma"][:]
            self.dl = f["dl"][:]
            self.lamb = f["lamb"][:]
            self.alpha = f["alpha"][:]
            self.logli = f["E_log_likelihood"][:]

class SkewTUniformMixture:
    """
    SkewTUniformMixture
    ===================
    A mixture model for clustering using the skewed Student's t-distribution.

    Parameters
    ==========
    n_cluster : int
        Number of clusters.
    init_method : str, default='gmm'
        Initialization method. Options: 'gmm', 'kmeans', 'params'.
    parametre : dict, optional
        Dictionary of initial parameters if init_method='params'.
    n_init_gmm : int, default=6
        Number of initializations for GMM.

    Attributes
    ==========
    mean : ndarray
        Cluster means.
    sigma : ndarray
        Cluster standard deviations.
    dl : ndarray
        Degrees of freedom for each cluster.
    lamb : ndarray
        Skewness parameters for each cluster.
    alpha : ndarray
        Cluster weights.
    tik : ndarray
        Posterior probabilities.
    logli : list
        Log-likelihood values during training.


    Notes
    =====

    For more information, refer to the documentation :ref:`doc.mixture.SkewTUniformMixture`

    Examples
    ========
    >>> import numpy as np
    >>> from cassiopy.mixture import SkewTUniformMixture
    >>> X = np.array([[5, 3], [5, 7], [5, 1], [20, 3], [20, 7], [20, 1]])
    >>> model = SkewTUniformMixture(n_cluster=2, init_method='kmeans')
    >>> model.fit(X, max_iter=100, tol=1e-4)
    >>> model.mean
    array([[ 5.        ,  1.40735413],
       [20.00000058,  0.66644041]])
    >>> model.predict_proba(np.array([[0, 0], [22, 5]]))
    array([[0.5, 0.5],
       [0.5, 0.5]])
    >>> model.save('model.h5')
    >>> model.load('Models_folder/model.h5')
    >>> model.predict_cluster(np.array([[0, 0], [22, 5]]))
    array([0., 0.])
    """

    def __init__(self, n_cluster:int, init_method='gmm', parametre=None, n_init_gmm=6):
        self.n_cluster = n_cluster
        self.init_method = init_method


        if self.init_method == "params":
            self.params = parametre

        if self.init_method == "gmm":
            self.n_init_gmm = n_init_gmm

    def initialisation_gmm(self, X):
        """
        Initialize the parameters for the Gaussian Mixture Model (GMM).

        Parameters
        ==========
        X : array-like of shape (n_samples, n_features)
            Input data matrix.

        Returns
        =======
        w : ndarray of shape (n_clusters,)
            Cluster weights.

        mu : ndarray of shape (n_clusters, n_features)
            Cluster means.

        s : ndarray of shape (n_clusters, n_features)
            Cluster standard deviations.

        nu : ndarray of shape (n_clusters, n_features)
            Degrees of freedom for each cluster.

        la : ndarray of shape (n_clusters, n_features)
            Skewness parameters for each cluster.
        
        """
        from sklearn.mixture import GaussianMixture

        gmm = GaussianMixture(n_components=self.n_cluster, covariance_type='diag').fit(X)
        mu = gmm.means_
        s = np.sqrt(gmm.covariances_)
        w = gmm.weights_

        w = np.append(w, 0.2) #add uniform cluster
        w = w/ np.sum(w)

        la = np.random.uniform(low=0, high=5, size=(self.n_cluster, X.shape[1]))
        nu = np.random.uniform(0, 10, size=(self.n_cluster, X.shape[1]))
        return w, mu, s, nu, la
    
    def initialisation_kmeans(self, X):
        """
        Initializes the parameters for the SkewMM algorithm using the K-means initialization method.

        Parameters
        ==========
        X : array-like of shape (n_samples, n_features)
            The input data matrix.

        default_n_init : int, default='auto'
            The number of times the K-means algorithm will be run with different centroid seeds. Default is 'auto'.

        Returns
        =======
        dict : dict
            A dictionary containing the initialized parameters:

        w : ndarray of shape (n_clusters,)
            Cluster weights.

        mu : ndarray of shape (n_clusters, n_features)
            Cluster means.
        
        s : ndarray of shape (n_clusters, n_features)
            Cluster standard deviations.

        nu : ndarray of shape (n_clusters, n_features)
            Degrees of freedom for each cluster.
            
        la : ndarray of shape (n_clusters, n_features)
            Skewness parameters for each cluster.
        """
        from sklearn.cluster import KMeans

        kmeans = KMeans(n_clusters=self.n_cluster, n_init=20).fit(X)
        mu = kmeans.cluster_centers_
        s = np.ones((self.n_cluster, X.shape[1]))
        w = np.bincount(kmeans.labels_) / len(kmeans.labels_)
        w = np.append(w, 0.2) #add uniform cluster
        w = w/ np.sum(w)
        la = np.random.uniform(low=1e-6, high=1e-5, size=(self.n_cluster, X.shape[1]))
        nu = np.random.uniform(0, 10, size=(self.n_cluster, X.shape[1]))
        return w, mu, s, nu, la

    def initialisation_random(self, X):
        """
        Initialize the parameters randomly for the SkewMM algorithm.

        Parameters
        ==========
        X : array-like of shape (n_samples, n_features)
            Input data matrix.

        Returns
        =======
        w : ndarray of shape (n_clusters,)
            Cluster weights.

        mu : ndarray of shape (n_clusters, n_features)
            Cluster means.

        s : ndarray of shape (n_clusters, n_features)
            Cluster standard deviations.

        nu : ndarray of shape (n_clusters, n_features)
            Degrees of freedom for each cluster.

        la : ndarray of shape (n_clusters, n_features)
            Skewness parameters for each cluster.
        
        """
        w = np.random.uniform(0.1, 1.0, size=self.n_cluster)
        w /= np.sum(w)

        mu = np.random.uniform(np.min(X, axis=0), np.max(X, axis=0), size=(self.n_cluster, X.shape[1]))
        s = np.random.uniform(0.1, 1.0, size=(self.n_cluster, X.shape[1]))
        nu = np.random.uniform(4., 10., size=(self.n_cluster, X.shape[1]))
        la = np.random.uniform(-2., 2., size=(self.n_cluster, X.shape[1]))

        return w, mu, s, nu, la
    
    def logt_expr(self, eta2, nu):
        return loggamma((nu + 1)/2) - loggamma(nu/2) - 0.5 * np.log(nu * np.pi) - ((nu + 1)/2) * np.log(1 + eta2 / nu)

    def ST(self, X, mu, s, nu, la): 
        """
        Compute the posterior probabilities for the SkewT mixture model.

        Parameters
        ==========
        X : ndarray
            Input data.

        w : ndarray
            Cluster weights.

        mu : ndarray
            Cluster means.

        s : ndarray
            Cluster standard deviations.

        nu : ndarray
            Degrees of freedom for each cluster.

        la : ndarray
            Skewness parameters for each cluster.

        Returns
        =======
        Z : ndarray
            Posterior probabilities for each cluster.
        """
        Skew = np.ones((self.n_cluster, X.shape[0])) 
        
        if X.ndim == 1:
            eta = (X[None, :] - mu[:, None]) / s[:, None]
            logt_val = self.logt_expr(eta**2, nu[:, None])

            lau = la[:, None] * eta
            t0 = (nu[:, None] + 1) / (nu[:, None]+ eta**2)
            c0 = lau * np.sqrt(t0)
            Tc0 = t.cdf(c0, df=nu[:, None] + 1)
            Skew = 2 * np.exp(logt_val) * Tc0 / s[:, None]
            
        else:
            for j in range(X.shape[1]):

                eta = (X[:, j][None, :] - mu[:, j][:, None]) / s[:, j][:, None]
                logt_val = self.logt_expr(eta**2, nu[:, j][:, None])

                lau = la[:, j][:, None] * eta
                t0 = (nu[:, j][:, None] + 1) / (nu[:, j][:, None]+ eta**2)
                c0 = lau * np.sqrt(t0)

                Tc0 = t.cdf(c0, df=nu[:, j][:, None] + 1)

                Skew *= 2 * np.exp(logt_val) * Tc0 / s[:, j][:, None]


        return Skew

    def LL(self, Z):
        """
        Compute the log-likelihood of the model.

        Parameters
        ==========

        Z : ndarray
            Posterior probabilities for each cluster.

        Returns
        =======
        logli_new : float
            Log-likelihood of the model.
        """
        ind_den = np.sum(Z, axis=0)
        logli_new = np.sum(np.log(ind_den), axis=0)
        return logli_new
    
    def phi(self, x, alpha, mean, sig, dl, lamb):
        """
        Compute the posterior probabilities for the SkewT mixture model.
        
        Parameters
        ==========
        x : array-like, shape (n_samples, n_features)
            The input data.
        alpha : array-like, shape (n_clusters,)
            The weights of the clusters.
        mean : array-like, shape (n_clusters, n_features)
            The means of the clusters.
        sig : array-like, shape (n_clusters, n_features)
            The standard deviations of the clusters.
        dl : array-like, shape (n_clusters, n_features)
            The degrees of freedom for each cluster.
        lamb : array-like, shape (n_clusters, n_features)
            The skewness parameters for each cluster.

        Returns
        =======
        p : array-like, shape (n_clusters, n_samples)
            The posterior probabilities for each cluster.
        """
        p=np.zeros((self.n_cluster+1, x.shape[0]))
        p[:-1, :]=alpha[:-1][:, None] * self.ST( x[:, :], mean[:, :], sig[:, :], dl, lamb) 

        volume = np.prod(x.max(axis=0) - x.min(axis=0))
        p[-1, :] = alpha[-1] / volume
        
        p = np.maximum(p, 1e-30)
        return p

    def fit(self, X, tol=1e-6, max_iter=200, init_method='gmm', parametre=None, verbose=0):
        """
        Fit the SkewT mixture model to the data.
        
        Parameters
        ==========
        X : array-like, shape (n_samples, n_features)
            The input data.

        tol : float, default=1e-6
            Tolerance for convergence.

        max_iter : int, default=200
            Maximum number of iterations for the EM algorithm.

        """
        if self.init_method == 'gmm':
            best_params = None
            best_LL = -np.inf
            params_to_test = [
                    self.initialisation_gmm(X) for _ in range(self.n_init_gmm)
                ]
            
            for params in params_to_test:
                w, mu, s, nu, la = params
                Z = self.phi(X, w, mu, s, nu, la)
                LL = self.LL(Z)
                if LL > best_LL:
                    best_LL = LL
                    best_params = params
            w, mu, s, nu, la = best_params
        
        elif self.init_method == 'kmeans':
            w, mu, s, nu, la = self.initialisation_kmeans(X)

        elif self.init_method == 'random':
            w, mu, s, nu, la = self.initialisation_random(X)

        elif self.init_method == 'parametre':
            w = parametre['alpha']
            mu = parametre['mu']
            s = parametre['sig']
            la = parametre['lamb']
            nu = parametre['nu']

        else : 
            raise ValueError(f"Error: The initialization method {self.init_method} is not recognized, please choose from 'params', 'kmeans', 'random' or 'gmm' ")

        if X.ndim == 1:
            n, dim = len(X), 1
        else:
            n, dim = X.shape[0], X.shape[1]


        iter = 0


        eta = (X[:, :][None, :] - mu[:, :][:, None]) / s[:, :][:, None]
        eta2 = eta**2
        lau = la[:, None] * eta
        t0 = (nu[:, None] + 1) / (nu[:, None] + eta2)
        c0 = lau * np.sqrt(t0)
        Tc0 = t.cdf(c0, df=nu[:, None] + 1)
        Z = self.phi(X, w, mu, s, nu, la)
        logli_old = self.LL(Z)
        self.logli = [self.LL(Z)]


        while True:
            # E-step
            if verbose==1:
                print(f'iteration: {iter}/{max_iter}')

            iter += 1
            ind_den = np.sum(Z, axis=0)
            
            Z /= ind_den

            c2 = la[:, None] * eta * np.sqrt((nu[:, None] + 3) / (nu[:, None] + eta2))
            Tc2 = t.cdf(c2, df=nu[:, None] + 3)
            tau = t0 * Tc2 / Tc0
            de = la / np.sqrt(1 + la**2)
            al = s[:, :] * de
            hs1 = (lau * tau + t.pdf(c0, df=nu[:, None] + 1) / Tc0 * np.sqrt(t0)) * np.sqrt(1 - de[:, None]**2)
            hs2 = 1 - de[:, None]**2 + de[:, None] * eta * hs1


            # M-step
            ni= np.sum(Z, axis=1)
            w = ni / n
        
            # Mise a jour de la skew
            mu[:, :] = np.sum(Z[:-1, :, None] * (tau * X[:, :] - (al[:, None] * hs1)), axis=1) / np.sum(Z[:-1, :, None] * tau, axis=1)
            cent = (X[:, :][None, :] - mu[:, :][:, None])
            Szs2 = np.sum(Z[:-1, :, None] * hs2, axis=1)
            al = np.sum(Z[:-1, :, None] * hs1 * cent, axis=1) / Szs2


            ka2 = np.sum(Z[:-1, :, None] * (tau * cent**2 - 2 * al[:, None] * hs1 * cent + (al**2)[:, None] * hs2), axis=1) / ni[:-1, None]
            s[:, :] = np.sqrt(ka2 + al**2)
            de = al / s[:, :]
            la = de / np.sqrt(1 - de**2)


            for i in range(self.n_cluster):
                if dim == 1:
                    def CML_nu(v):
                        cdf_vals = t.cdf(la[i] * np.sqrt((v + 1) / (v + eta2[i, :])), df=v + 1)
                        log_t = self.logt_expr(eta2[i, :], v)
                        return -np.sum(Z[i, :] * (log_t + np.log(cdf_vals)))
                    res = minimize_scalar(CML_nu, bounds=(1e-6, 100), method='bounded')
                    nu[i] = res.x
                else:
                    for j in range(dim):
                        def CML_nu(v):
                            cdf_vals = t.cdf(la[i, j] * np.sqrt((v + 1) / (v + eta2[i, :, j])), df=v + 1)
                            log_t = self.logt_expr(eta2[i, :, j], v)
                            return -np.sum(Z[i, :] * (log_t + np.log(cdf_vals)))
                        res = minimize_scalar(CML_nu, bounds=(1e-6, 100), method='bounded')
                        nu[i, j] = res.x


            eta = (X[:, :][None, :] - mu[:, :][:, None]) / s[:, :][:, None]
            eta2 = eta**2
            lau = la[:, None] * eta
            t0 = (nu[:, None] + 1) / (nu[:, None] + eta2)
            c0 = lau * np.sqrt(t0)
            Tc0 = t.cdf(c0, df=nu[:, None] + 1)
            Z = self.phi(X, w, mu, s, nu, la)

            
            logli_new = self.LL(Z)

            diff = logli_new - logli_old
            if diff < tol or iter >= max_iter:
                print('tolérance atteinte')
                break

            if logli_new < logli_old:
                print('logli_new', logli_new)
                print('logli_old', logli_old)
                print('diminution du logli')
                break

            if iter == max_iter:
                print('nombre d iterations atteint')
                break
            
            logli_old = logli_new
            self.logli.append(logli_new)

        ind_den = np.sum(Z, axis=0)
        Z /= ind_den

        self.tik = Z/ ind_den

        self.mean = mu
        self.sigma = s
        self.dl = nu
        self.lamb = la
        self.alpha = w

        return self

    def predict_proba(self, X):
        """
        Predict the posterior probabilities for the data.

        Parameters
        ==========
        X : array-like, shape (n_samples, n_features)
            The input data.

        Returns
        =======
        proba : ndarray, shape (n_samples, n_clusters)
            The posterior probabilities for each cluster.
        """
        # Implementation of the predict_proba method
        Z = self.phi(X, self.alpha, self.mean, self.sigma, self.dl, self.lamb)
        ind_den = np.sum(Z, axis=0)
        proba = Z / ind_den
        return proba
    
    def predict(self, X):
        """
        Predict the cluster labels for the data.

        Parameters
        ==========
        - X (array-like): The input data.

        Returns
        =======
        - labels (array-like): The predicted cluster labels.
        """
        # Implementation of the predict method
        proba = self.predict_proba(X)
        labels=np.array([])
        for i in range(proba.shape[1]):
            labels = np.append(labels, np.argmax(proba[:, i]))
        return labels    
         
    def ARI(self, y_true, y_pred):
        """
        Compute the ARI .

        Parameters
        ==========
        - y (array-like): The true labels.

        Returns
        =======
        - ari (float): The Adjusted Rand Index (ARI) score.
        """
        from sklearn.metrics import adjusted_rand_score
        ari = adjusted_rand_score(y_true, y_pred)

        return ari

    def confusion_matrix(self, y_true, y_pred):

        """
        Calculate the confusion matrix.

        Parameters
        ==========
        y_true : array-like
            The true labels.

        y_pred : array-like, default=None
            The predicted labels.

        Returns
        =======
        matrix : array-like
            The confusion matrix. The last cluster correspond to the uniform cluster.
        """

        if y_true is None:
            raise ValueError("Error: The true labels are missing, please provide them.")

        y_true = y_true.astype(int)


        y_pred = np.array(y_pred).astype(int)

        # Obtenez les classes uniques
        classes = np.unique(np.concatenate((y_true, y_pred)))


        # Créez une matrice de confusion initialisée à zéro
        matrix = np.zeros((len(np.unique(y_true)), self.n_cluster+1), dtype=int)

        # Utilisez np.searchsorted pour obtenir les indices des classes
        true_indices = np.searchsorted(classes, y_true)
        pred_indices = np.searchsorted(classes, y_pred)

        # Mettez à jour la matrice de confusion en comptant les occurrences
        for true_idx, pred_idx in zip(true_indices, pred_indices):
            matrix[true_idx, pred_idx] += 1

        return matrix
    
    def BIC(self, X):
        """
        Calculate the Bayesian Information Criterion (BIC) for the model.

        Parameters
        ==========
        - X (array-like): The input data.

        Returns
        =======
        - bic (float): The BIC value.
        """
        # Implementation of the BIC method
        n = X.shape[0]
        LL = self.logli[-1]

        m = 4 * self.n_cluster
        bic = -2 * LL + np.log(n) * m

        return bic
    
  
    def AIC(self, X, penalty_weight=0.1):
        from collections import Counter
        # Implementation of the BIC method
        y_pred = self.predict(X)
        n = X.shape[0]
        LL = self.logli[-1]

        m = 4 * self.n_cluster
        aic = -2 * LL + 2* m

        cluster_sizes = Counter(y_pred)
        penalty = sum(1 for size in cluster_sizes.values() if size < 5)
        return aic * (1 - penalty_weight * penalty)

    def IUS(self, X, y_pred, bins=3):
        """
        Calcule l'entropie de Shannon pour des données multidimensionnelles
        en utilisant une estimation par histogramme.

        Paramètres :
        - data : ndarray de forme (n_samples, n_features)
        - bins : nombre de divisions par dimension (ou liste)

        Retourne :
        - entropie de Shannon (en bits)
        """
        probabilites= self.tik[-1,:]

        tirage_bernoulli = np.random.binomial(1, probabilites)

        label_bernouilli = np.zeros(X.shape[0])

        for i in range(X.shape[0]):
            if tirage_bernoulli[i]==1:
                label_bernouilli[i]= self.n_cluster
            else:
                label_bernouilli[i]=y_pred[i]

        data = X[:, :][label_bernouilli == self.n_cluster]

        # Histogramme multidimensionnel
        hist, edges = np.histogramdd(data, bins=bins)

        # Probabilités (normalisation)
        prob = hist / np.sum(hist)

        # Entropie (en bits)
        prob_nonzero = prob[prob > 0]
        H = -np.sum(prob_nonzero * np.log2(prob_nonzero))

        # Entropie maximale = log2(N) où N est le nombre total de cases non nulles
        N = np.sum(hist)
        H_max = np.log2(N) if N > 0 else 1e-12  # pour éviter la division par zéro

        # Indice d’uniformité
        iuS = H / H_max if H_max > 0 else 0

        return iuS
    
    def KL(self, X, bins=3):
        from scipy.special import rel_entr
        y_pred = self.predict(X)
        probabilites= self.tik[-1,:]

        tirage_bernoulli = np.random.binomial(1, probabilites)

        label_bernouilli = np.zeros(X.shape[0])

        for i in range(X.shape[0]):
            if tirage_bernoulli[i]==1:
                label_bernouilli[i]= self.n_cluster
            else:
                label_bernouilli[i]=y_pred[i]

        data = X[:, :][label_bernouilli == self.n_cluster]

        hist, _ = np.histogramdd(data, bins=bins)
        prob = hist / np.sum(hist)
        
        uniform_prob = 1 / np.prod(hist.shape)
        kl_div = np.sum(rel_entr(prob, uniform_prob))
        
        return kl_div
    
    def L2(self, X, bins=10, penalty_weight=0.1):
        from scipy.spatial.distance import cdist
        from collections import Counter
        y_pred = self.predict(X)
        probabilites= self.tik[-1,:]

        tirage_bernoulli = np.random.binomial(1, probabilites)

        label_bernouilli = np.zeros(X.shape[0])

        for i in range(X.shape[0]):
            if tirage_bernoulli[i]==1:
                label_bernouilli[i]= self.n_cluster
            else:
                label_bernouilli[i]=y_pred[i]

        
        data = X[:, :][label_bernouilli == self.n_cluster]

        # min_vals = np.min(data, axis=0)
        # max_vals = np.max(data, axis=0)
        # data = (data - min_vals) / (max_vals - min_vals + 1e-12)
    
        hist, _ = np.histogramdd(data, bins=bins)
        prob = hist / np.sum(hist)
        
        uniform_prob = 1 / np.prod(hist.shape)
        l2_distance = np.sqrt(np.sum((prob - uniform_prob) ** 2))

        cluster_sizes = Counter(y_pred)
        penalty = sum(1 for size in cluster_sizes.values() if size < 5)
        return l2_distance * (1 - penalty_weight * penalty)
    

    def chi2(self, X, bins=3):
        from scipy.stats import chisquare
        y_pred = self.predict(X)
        probabilites= self.tik[-1,:]

        tirage_bernoulli = np.random.binomial(1, probabilites)

        label_bernouilli = np.zeros(X.shape[0])

        for i in range(X.shape[0]):
            if tirage_bernoulli[i]==1:
                label_bernouilli[i]= self.n_cluster
            else:
                label_bernouilli[i]=y_pred[i]

        
        data = X[:, [0,1,3]][label_bernouilli == self.n_cluster]
        hist, _ = np.histogramdd(data, bins=bins)
        observed = hist.flatten()
        expected = np.full_like(observed, np.mean(observed))
        chi2_stat, p_value = chisquare(f_obs=observed, f_exp=expected)
        return chi2_stat, p_value 

    def HARTIGAN(self, X):
        W = 0
        y_pred = self.predict(X)
        for cluster_id in np.unique(y_pred):
            cluster_points = X[y_pred == cluster_id]
            if len(cluster_points) == 0:
                continue  # éviter les clusters vides
            center = cluster_points.mean(axis=0)
            distances = np.linalg.norm(cluster_points - center, axis=1)
            W += np.sum(distances ** 2)
        return W
    
    def save(self, filename: str):
        """
        Save the model to a file.

        Parameters
        ==========
        filename : str
            The name of the file.
        """
        import h5py

        if not filename.endswith(".h5"):
            filename = f"{filename}.h5"

        if not filename:
            raise ValueError(
                "Error: The filename is empty, please provide a valid filename."
            )

        if not os.path.exists("Models_folder"):
            os.makedirs("Models_folder")

        with h5py.File(f"Models_folder/{filename}", "w") as f:
            f.create_dataset("mean", data=self.mean)
            f.create_dataset("sigma", data=self.sigma)
            f.create_dataset("dl", data=self.dl)
            f.create_dataset("lamb", data=self.lamb)
            f.create_dataset("alpha", data=self.alpha)
            f.create_dataset("tik", data=self.tik)
            f.create_dataset("E_log_likelihood", data=self.logli)

    def load(self, filename: str):
        """
        Load matrices from a given file.

        Parameters
        ==========
        filename : str
            The path to the file containing the matrices.
        """
        import h5py

        with h5py.File(filename, "r") as f:
            self.mean = f["mean"][:]
            self.sigma = f["sigma"][:]
            self.dl = f["dl"][:]
            self.lamb = f["lamb"][:]
            self.alpha = f["alpha"][:]
            self.logli = f["E_log_likelihood"][:]