# PyTSML
# For information about the license, check: https://github.com/Bl0tniaQus/PyTSML
import numpy as np
from scipy.linalg import svd
from fastdtw import fastdtw
import random
import warnings
warnings.filterwarnings('ignore')
class LDMLT:
    def __init__(self, triplets_factor = 20, cycles = 3, alpha_factor = 5):
        self.triplets_factor = triplets_factor
        self.cycles = cycles
        self.alpha_factor = alpha_factor
        self.M = None
        self.X = None
        self.Y = None
    def DTW(self, MTS_1, MTS_2, distOnly = False):
        MTS_1 = MTS_1.T
        MTS_2 = MTS_2.T
        _, col_1 = MTS_1.shape
        row, col_2 = MTS_2.shape
        d = np.zeros((col_1, col_2))
        D1 = MTS_1.T @ self.M @ MTS_1
        D2 = MTS_2.T @ self.M @ MTS_2
        D3 = MTS_1.T @ self.M @ MTS_2
        d = np.array([[D1[i, i] + D2[j, j] - 2 * D3[i, j] for j in range(col_2)] for i in range(col_1)])
        D = np.zeros_like(d)
        for m in range(col_1):
            for n in range(col_2):
                if m == 0 and n == 0:
                    D[m, n] = d[m, n]
                elif m == 0 and n > 0:
                    D[m, n] = d[m, n] + D[m, n-1]
                elif n == 0 and m > 0:
                    D[m, n] = d[m, n] + D[m-1, n]
                else:
                    D[m, n] = d[m, n] + min(D[m-1, n], min(D[m-1, n-1], D[m, n-1]))
        
        Dist = D[col_1-1, col_2-1]
        if distOnly:
            return Dist, None, None
        n = col_2 - 1
        m = col_1 - 1
        k = 1
        w = np.array([col_1-1, col_2-1])
        while (n + m) != 0:
            if n == 0:
                m -= 1
            elif m == 0:
                n -= 1
            else:
                number = np.argmin((D[m-1, n], D[m, n-1], D[m-1, n-1]))
                if number == 0:
                    m -= 1
                elif number == 1:
                    n -= 1
                else:
                    m -= 1
                    n -= 1
            k += 1
            w = np.vstack((np.array([m, n]), w))
        
        MTS_E1 = np.zeros((row, k))
        MTS_E2 = np.zeros((row, k))
        for i in range(row):
            MTS_E1[i, :] = MTS_1[i, w[:, 0].astype(int)]
            MTS_E2[i, :] = MTS_2[i, w[:, 1].astype(int)]
        return Dist, MTS_E1, MTS_E2
    def predict(self, X, k = 3):
        if not isinstance(X, list):
            if len(X[0].shape) == 1:
                X = np.array([X])
        X = [np.array(X[i].copy()) for i in range(len(X))]
        n_train = len(self.X)
        n_test = len(X)
        Y_kind = np.unique(self.Y)
        Pred_Y = np.zeros(n_test)
        for index_test in range(n_test):
            Distance = np.zeros(n_train)
            for index_train in range(n_train):
                Dist, _, _= self.DTW(self.X[index_train], X[index_test], distOnly = True)
                Distance[index_train] = Dist
            Inds = np.argsort(Distance,stable=True)
            
            counts = np.zeros(len(Y_kind))
            for j in range(k):
                counts[np.nonzero(Y_kind == self.Y[Inds[j]])] += 1
            ids = np.argwhere(counts == np.amax(counts))
            if len(ids) == 1:
                Pred_Y[index_test] = Y_kind[np.argmax(counts)]
            else:
                Pred_Y[index_test] = self.Y[Inds[0]]
        if len(Pred_Y) == 1:
            Pred_Y = Pred_Y[0]
        return Pred_Y
        
    def fit(self, X, Y, M = None):
        passed_M = True
        try:
            _ = M.shape
        except:
            passed_M = False
        self.X = [np.array(X[i].copy()) for i in range(len(X))]
        self.Y = Y.copy()
        if not passed_M:
            num_candidates = len(self.X)
            num_features = len(self.X[0][0])
            triplets_factor = self.triplets_factor
            self.M = np.eye(num_features, num_features)
            Y_kind = np.unique(self.Y)
            X_n, Y_n = self.dataRank(self.X, self.Y, Y_kind)
            S = np.zeros((num_candidates, num_candidates))
            for i in range(num_candidates):
                for j in range(num_candidates):
                    if Y_n[i] == Y_n[j]:
                        S[i, j] = 1
            
            Triplet, rho, Error_old = self.selectTriplets(X_n, triplets_factor, Y_n, S)
            
            iter_count = len(Triplet)
            total_iter = iter_count
            for i in range(self.cycles):
                alpha = self.alpha_factor / iter_count
                rho = 0
                self.updateM(X_n, Triplet, alpha, rho)
                Triplet, rho, Error_new = self.selectTriplets(X_n, triplets_factor, Y_n, S)
                iter_count = len(Triplet)
                total_iter += iter_count
                triplets_factor = Error_new / Error_old * triplets_factor
                cov = (Error_old - Error_new) / Error_old
                if abs(cov) < 10e-5:
                    break
                Error_old = Error_new
        else:
            if M.shape[0] == X[0].shape[1]:
                self.M = M.copy()
            else:
                raise ValueError("Invalid M Size")
    def updateM(self, X, triplet, gamma, rho):
        self.M = self.M / np.trace(self.M)
        i = 0
        options = np.zeros(5)
        options[4] = 1
        while i < len(triplet):
            i1 = triplet[i, 0]
            i2 = triplet[i, 1]
            i3 = triplet[i, 2]
            Dist1, swi1, swi2 = self.DTW(X[i1], X[i2])
            P = swi1 - swi2
            Dist2, swi1, swi3 = self.DTW(X[i1], X[i3])
            Q = swi1 - swi3
            IP = np.eye(P.shape[1])
            IQ = np.eye(Q.shape[1])
        
            if Dist2 - Dist1 < rho:
                alpha = gamma / np.trace(np.linalg.inv(np.eye(self.M.shape[0]) - self.M) @ self.M @ Q @ Q.T)
                M_temp = self.M - alpha * self.M @ P @ np.linalg.inv(IP + alpha * P.T @ self.M @ P) @ P.T @ self.M
                self.M = M_temp + alpha * M_temp @ Q @ np.linalg.inv(IQ - alpha * Q.T @ M_temp @ Q) @ Q.T @ M_temp
                L, S, R = svd(self.M)
                self.M = self.M / np.sum(np.diag(S))
                self.M = self.M / np.trace(self.M)
            i += 1
        self.M = self.M * self.M.shape[0]
    def dataRank(self, X, Y, Y_kind):
        X_data = []
        Y_data = []
        for l in range(len(Y_kind)):
            index = np.nonzero(Y == Y_kind[l])[0]
            X_data.extend([X[i] for i in index])
            Y_data.extend([Y[i] for i in index])
        return X_data, Y_data
    def orderCheck(self, X, Y):
        numberCandidate = len(X)
        compactfactor = 2
        Y_kind = np.sort(np.unique(Y))
        index = 0
        j = 0
        map_vector = np.zeros(numberCandidate, dtype=int)
        for i in range(numberCandidate):
            if Y[i] == Y[index] and j < compactfactor:
                map_vector[i] = index
                j += 1
            else:
                index += j
                map_vector[i] = index
                j = 1
        
        map_vector_kind = np.unique(map_vector)
        map_vector_kind_length = len(map_vector_kind)
        S = np.zeros((map_vector_kind_length, map_vector_kind_length))
        for i in range(map_vector_kind_length):
            for j in range(i):
                if Y[map_vector_kind[i]] == Y[map_vector_kind[j]]:
                    S[i, j] = 1
                    S[j, i] = 1
            S[i,i] = 1
        
        Distance = np.zeros((map_vector_kind_length,map_vector_kind_length))
        for i in range(len(map_vector_kind)):
            for j in range(i, len(map_vector_kind)):
                Dist, _, _ = self.DTW(X[map_vector_kind[i]], X[map_vector_kind[j]], distOnly = True)
                Distance[i, j] = Dist
                Distance[j, i] = Dist
        Disorder = np.zeros(numberCandidate)
        for i in range(len(map_vector_kind)):
            Distance_i = Distance[i, :]
            S_i = S[i, :]
            index_ascend = np.argsort(Distance_i, stable=True)
            S_new = S_i[(index_ascend)]
            sum_in = np.sum(S_new == 1)
            rs1 = sum_in
            rs2 = 0
            for j in range(len(map_vector_kind)):
                if S_new[j] == 0:
                    rs2 += rs1
                else:
                    rs1 -= 1
            index = np.nonzero(map_vector == map_vector_kind[i])[0]
            Disorder[index] = rs2
        Distance_Extended = np.zeros((numberCandidate,numberCandidate))
        for i in range(len(map_vector_kind)):
            index_i = np.where(map_vector == map_vector_kind[i])[0]
            for j in range(i, len(map_vector_kind)):
                index_j = np.where(map_vector == map_vector_kind[j])[0]
                Distance_Extended[np.ix_(index_i,index_j)] = Distance[i, j]
                Distance_Extended[np.ix_(index_j,index_i)] = Distance[j, i]
        return Distance_Extended, Disorder
    def selectTriplets(self, X, factor, Y, S):
        bias = 3
        numberCandidate = len(X)
        triplet = []
        Distance, Disorder = self.orderCheck(X, Y)
        f, c = np.histogram(Distance, bins=100)
        l = c[20]
        u = c[80]
        rho = u - l
        error = np.sum(Disorder)
        Disorder = Disorder / (np.sum(Disorder) + np.finfo(float).eps)
        Triplet_N = factor * numberCandidate
        for l in range(numberCandidate):
            Sample_Length = round(np.sqrt(Disorder[l] * Triplet_N))
            if Sample_Length < 1:
                continue
            S_l = S[l, :]
            Distance_l = Distance[l, :]
            index_in = np.nonzero(S_l == 1)[0]
            index_out = np.nonzero(S_l == 0)[0]
            index_descend = np.argsort(-Distance_l[index_in])
            index_ascend = np.argsort(Distance_l[index_out])
            triplet_itemi = l
            triplet_itemj = index_in[index_descend[bias:min(bias + Sample_Length, len(index_in))]]
            triplet_itemk = index_out[index_ascend[bias:min(bias + Sample_Length, len(index_out))]]
            itemi, itemj, itemk = np.meshgrid(triplet_itemi, triplet_itemj, triplet_itemk)
            new_triplet = np.column_stack((itemi.flatten(order="F"), itemj.flatten(order="F"), itemk.flatten(order="F")))
            if len(triplet)==0:
                triplet = new_triplet
            else:
                triplet = np.concatenate((triplet, new_triplet), axis=0)
        return triplet, rho, error
    def saveM(self, filename, delimiter = " "):
        np.savetxt(filename, self.M, delimiter = delimiter) 
    @staticmethod
    def loadM(filename, delimiter = " "):
        M = np.loadtxt(filename, delimiter = delimiter)
        return M

class DDE:
    def __init__(self, DE_step = 3, DE_dim = 2, DE_slid = 2, alpha = 2, beta = 3, grid_size = 0.1, filter_param = 0.5):
        self.DE_step = DE_step
        self.DE_dim = DE_dim
        self.DE_slid = DE_slid
        self.alpha = alpha
        self.beta = beta
        self.filter_param = filter_param
        self.grid_size = grid_size
        self.Trans = None
        self.classLabels = None
        self.Grid = None
        self.X = None
        self.Y = None
    def fit(self, X, Y):
        self.X = [np.array(X[i].copy()) for i in range(len(X))]
        self.Y = Y.copy()
        self.classLabels = np.unique(self.Y)
        n_class = len(self.classLabels)
        n_dimSignal = self.X[0].shape[1]
        self.Trans = {}
        if self.grid_size >0:
            self.Grid = {'size' : self.grid_size, 'center' : np.zeros(self.DE_dim * n_dimSignal)}
        for y in self.classLabels:
            self.Trans[y] = []
        for loop in range(len(self.X)):
            x = self.X[loop].T
            for i in range(x.shape[0]):
                x[i, :], _ = self.lowpass_filter(x[i, :], self.filter_param)
            y = self.Y[loop]
            point_cloud = self.delay_embedding_nd(x.T, self.DE_dim, self.DE_step, self.DE_slid)
            self.Trans[y] = self.add2Trans(point_cloud, self.Trans[y])
        for i in self.classLabels:
            self.Trans[i] = self.Trans_Prob(self.Trans[i])
        
    def predict(self, X):
        X_test = [np.array(X[i].copy()) for i in range(len(X))]
        if len(X_test[0].shape) == 1:
            X_test = np.array([X_test])
        predictions = [0 for i in range(len(X_test))]
        dist = {}
        for i in self.classLabels:
            dist[i] = 0
        for loop in range(len(X_test)):
            x = X_test[loop].T
            for i in range(x.shape[0]):
                x[i, :], _ = self.lowpass_filter(x[i, :], self.filter_param)
            point_cloud = self.delay_embedding_nd(x.T, self.DE_dim, self.DE_step, self.DE_slid)
            for i in self.classLabels:
                dist[i] = self.HDist(point_cloud, self.Trans[i], i, self.alpha, self.beta)
            dists = list(dist.values())
            loc = np.argmin(dists)
            predictions[loop] = self.classLabels[loc]
        if len(X_test) == 0:
            return predictions[0]
        return predictions
            
            
    def HDist(self, points, Trans, i, alpha=1.0, beta=1.0):
        
        p = Trans.shape[0]
        if p == 0:
            raise ValueError('Transition list is empty. Probably method arguments are invalid.')
        
        m, n = points.shape
        if m ==0:
            return np.nan
        
        if self.Grid is not None:
            gridCenter = self.Grid['center']
            gridSize = self.Grid['size']
            points = np.round((points - np.tile(gridCenter, (m, 1))) / np.tile(gridSize, (m, 1))) * np.tile(gridSize, (m, 1)) + np.tile(gridCenter, (m, 1))
        vec_Trans = Trans[:, n:2*n] - Trans[:, :n]
        loc_Trans = (Trans[:, n:2*n] + Trans[:, :n]) / 2
        len_Trans = np.sqrt(np.sum(vec_Trans**2, axis=1))

        vec_points = points[1:, :] - points[:-1, :]
        loc_points = (points[1:, :] + points[:-1, :]) / 2
        len_points = np.sqrt(np.sum(vec_points**2, axis=1))
        norm_angle = np.exp(np.real(np.arccos(vec_points @ vec_Trans.T / (np.outer(len_points, len_Trans)))))
        if np.sum(len_points == 0) > 0 and  np.sum(len_Trans == 0) > 0:
            ag_lp = np.argwhere(len_points == 0)
            ag_T = np.argwhere(len_Trans == 0)
            for i in ag_lp:
                for j in ag_T:
                    norm_angle[i, j] = 0
        norm_length = np.exp((np.tile(len_points[:, None], (1, p)) - 
                               np.tile(len_Trans[None, :], (m-1, 1)))**2 / 
                              (np.tile(len_points[:, None], (1, p))**2))
        norm_length[np.isnan(norm_length)] = 0

        norm_distance = np.zeros((m-1, p))
        for i in range(m-1):
            if len_points[i] > 0:
                norm_distance[i, :] = np.sqrt(np.sum((np.tile(loc_points[i, :], (p, 1)) - loc_Trans)**2, axis=1)) / len_points[i]
            else:
                norm_distance[i, :] = np.sqrt(np.sum((np.tile(loc_points[i, :], (p, 1)) - loc_Trans)**2, axis=1))

        norm_dist = norm_distance + alpha * norm_length + beta * norm_angle
        dist = np.nanmin(norm_dist, axis=1)
        return np.nanmean(dist[len_points > 0])
    def Trans_Prob(self, Trans):
        C, ic = np.unique(Trans, axis = 0, return_inverse=True)
        l = C.shape[0]
        counts = np.bincount(ic, minlength=l)
        prob = counts / counts.sum()
        if len(Trans) != 0:
            Trans = np.hstack((C, prob[:, np.newaxis]))
        else:
            return np.array(Trans)
        return Trans
    def add2Trans(self, points, Trans):
        if self.Grid is not None:
            m, n = points.shape
            gridCenter = self.Grid['center']
            gridSize = self.Grid['size']
            if len(self.Grid['center']) != n:
                gridCenter = np.tile(self.Grid['center'][0], (1, n))
            if self.Grid['size'] != n:
                gridSize = np.tile(self.Grid['size'], (1, n))
            temp = np.round((points - np.tile(gridCenter, (m, 1))) / np.tile(gridSize, (m, 1))) * np.tile(gridSize, (m, 1)) + np.tile(gridCenter, (m, 1))
        else:
            temp = points
        temp = np.hstack((temp[:-1, :], temp[1:, :]))
        if temp.shape[0] > 0:
            if len(Trans)!=0:
                Trans = np.vstack((Trans, temp))
            else:
                Trans = temp
        return Trans

    def delay_embedding(self, x, dim=2, step=1, w=1):

        if len(x) < 1:
            raise ValueError('Not enough input arguments')
        if dim < 1:
            raise ValueError('Too large dimension')
        n = len(x)
        if n < dim:
            raise ValueError('Too large dimension')
        d = round(((n - step * (dim - 1)) / w)+0.001)
        if d<0:
            d = 0
        y = np.full((d, dim), np.nan)
        ind = np.arange(0, n, w)
        for i in range(y.shape[0]):
            temp = x[ind[i]:ind[i] + step * dim:step]
            y[i, :] = np.reshape(temp, (1, len(temp)))
        
        return y
    def delay_embedding_nd(self, x, dim=2, step=1, w=1):
        if x is None:
            raise ValueError('Not enough input arguments')
        n, n_dim = x.shape
        if n < dim:
            raise ValueError('Too large dimension')
        y = []
        for i in range(n_dim):
            if len(y) == 0:
                y = self.delay_embedding(x[:, i], dim, step, w)
            else:
                y = np.hstack((y, self.delay_embedding(x[:, i], dim, step, w)))
        return np.array(y)

    def lowpass_filter(self, input_data, param, tol=100):
        output = input_data.copy()
        
        cnt = 0
        tag = True
        for i in range(1, len(input_data)):
            if abs(output[i-1] - input_data[i]) > tol:
                cnt += 1
                output[i] = output[i-1]
            else:
                output[i] = param * output[i-1] + (1 - param) * input_data[i]
        
        if cnt / len(input_data) > 0.5:
            raise ValueError("Invalid data")
            tag = False
        
        return output, tag
        
class DTW_KNN:
    def __init__(self):
        self.X = None
        self.Y = None
    def fit(self, X, Y):
        self.X = X.copy()
        self.Y = Y.copy()
    def dtw(self, a,b):
        dist, _ = fastdtw(a,b)
        return float(dist)
    def predict(self, X, k = 3):
        if not isinstance(X, list):
            if len(X[0].shape) == 1:
                X = np.array([X])
        n_train = len(self.X)
        n_test = len(X)
        Y_kind = np.unique(self.Y)
        Pred_Y = np.zeros(n_test)
        for index_test in range(n_test):
            Distance = np.zeros(n_train)
            for index_train in range(n_train):
                Dist = self.dtw(self.X[index_train], X[index_test])
                Distance[index_train] = Dist
            Inds = np.argsort(Distance,stable=True)
            counts = np.zeros(len(Y_kind))
            for j in range(k):
                counts[np.nonzero(Y_kind == self.Y[Inds[j]])] += 1
            ids = np.argwhere(counts == np.amax(counts))
            if len(ids) == 1:
                Pred_Y[index_test] = Y_kind[np.argmax(counts)]
            else:
                Pred_Y[index_test] = self.Y[Inds[0]]
        if len(Pred_Y) == 1:
            Pred_Y = Pred_Y[0]
        return Pred_Y
def generate_example_data(min_len, max_len, n_instances, n_classes):
    X = []
    Y = []
    for i in range(n_instances):
        instance = []
        label = random.randint(1,n_classes)
        length = random.randint(min_len, max_len)
        for j in range(length):
            noise = random.randint(-(10*label), 10*label) / 10
            f1 = (j/10) + noise
            f2 = (0 + (j%2)*2) + noise
            f3 = (0 + (j%2)*2*(not j%2)*(-1)) + noise
            instance.append([f1,f2,f3])
        X.append(instance)
        Y.append(label)
    return X, Y
def accuracy(predicted, true):
    lp = len(predicted)
    lt = len(true)
    if lp != lt:
        raise ValueError("Input vectors are not the same length!")
    counts = 0
    for i in range(lp):
        if predicted[i] == true[i]:
            counts += 1
    return counts/lp

