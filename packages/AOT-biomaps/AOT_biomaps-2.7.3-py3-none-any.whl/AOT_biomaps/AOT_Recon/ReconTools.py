from AOT_biomaps.Config import config

import torch
import numpy as np
from numba import njit, prange
import torch.nn.functional as F
if config.get_process()  == 'gpu':
    try:
        from torch_sparse import coalesce
    except ImportError:
        raise ImportError("torch_scatter and torch_sparse are required for GPU processing. Please install them using 'pip install torch-scatter torch-sparse' with correct link (follow instructions https://github.com/LucasDuclos/AcoustoOpticTomography/edit/main/README.md).")


@njit(parallel=True)
def _forward_projection(SMatrix, theta_p, q_p):
    t_dim, z_dim, x_dim, i_dim = SMatrix.shape
    for _t in prange(t_dim):
        for _n in range(i_dim):
            total = 0.0
            for _z in range(z_dim):
                for _x in range(x_dim):
                    total += SMatrix[_t, _z, _x, _n] * theta_p[_z, _x]
            q_p[_t, _n] = total

@njit(parallel=True)
def _backward_projection(SMatrix, e_p, c_p):
    t_dim, z_dim, x_dim, n_dim = SMatrix.shape
    for _z in prange(z_dim):
        for _x in range(x_dim):
            total = 0.0
            for _t in range(t_dim):
                for _n in range(n_dim):
                    total += SMatrix[_t, _z, _x, _n] * e_p[_t, _n]
            c_p[_z, _x] = total

@njit
def _build_adjacency_sparse_CPU(Z, X,corner = (0.5-np.sqrt(2)/4)/np.sqrt(2),face = 0.5-np.sqrt(2)/4):
    rows = []
    cols = []
    weights = []

    for z in range(Z):
        for x in range(X):
            j = z * X + x
            for dz in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dz == 0 and dx == 0:
                        continue
                    nz, nx = z + dz, x + dx
                    if 0 <= nz < Z and 0 <= nx < X:
                        k = nz * X + nx
                        weight = corner if abs(dz) + abs(dx) == 2 else face
                        rows.append(j)
                        cols.append(k)
                        weights.append(weight)

    index = (np.array(rows), np.array(cols))
    values = np.array(weights, dtype=np.float32)
    return index, values 

def _build_adjacency_sparse_GPU(Z, X,corner = (0.5-np.sqrt(2)/4)/np.sqrt(2),face = 0.5-np.sqrt(2)/4):
    rows = []
    cols = []
    weights = []

    for z in range(Z):
        for x in range(X):
            j = z * X + x
            for dz in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dz == 0 and dx == 0:
                        continue
                    nz, nx = z + dz, x + dx
                    if 0 <= nz < Z and 0 <= nx < X:
                        k = nz * X + nx
                        weight = corner if abs(dz) + abs(dx) == 2 else face
                        rows.append(j)
                        cols.append(k)
                        weights.append(weight)

    index = torch.tensor([rows, cols], device= config.select_best_gpu())
    values = torch.tensor(weights, dtype=torch.float32, device= config.select_best_gpu())
    index, values = coalesce(index, values, m=Z*X, n=Z*X)
    return index, values 


def power_method(P, PT, data, Z, X, n_it=10, isGPU=False):
    x = PT(data)
    x = x.reshape(Z, X)
    for _ in range(n_it):
        grad = gradient_gpu(x) if isGPU else gradient_cpu(x)
        div = div_gpu(grad) if isGPU else div_cpu(grad)
        x = PT(P(x.ravel())) - div.ravel()
        s = torch.sqrt(torch.sum(x**2))
        x /= s
        x = x.reshape(Z, X)
    return torch.sqrt(s)

def proj_l2(p, alpha):
    norm = torch.sqrt(torch.sum(p**2, dim=0, keepdim=True))
    return p * alpha / torch.max(norm, torch.tensor(alpha, device=p.device))

def norm2sq(x):
    return torch.sum(x**2)

def norm1(x):
    return torch.sum(torch.abs(x))

def gradient_cpu(x):
    grad_x = torch.zeros_like(x)
    grad_y = torch.zeros_like(x)

    grad_x[:-1, :] = x[1:, :] - x[:-1, :]
    grad_y[:, :-1] = x[:, 1:] - x[:, :-1]

    return torch.stack((grad_x, grad_y), dim=0)

def div_cpu(x):
    if x.dim() == 3:
        x = x.unsqueeze(0)  # Devient [1, 2, H, W]

    gx = x[:, 0:1, :, :]  # gradient horizontal
    gy = x[:, 1:2, :, :]  # gradient vertical

    # Définition des noyaux de divergence
    kernel_x = torch.tensor([[[[1.0], [-1.0]]]], dtype=torch.float32)
    kernel_y = torch.tensor([[[[1.0, -1.0]]]], dtype=torch.float32)

    # Appliquer la convolution
    div_x = F.conv2d(gx, kernel_x, padding=(1, 0))
    div_y = F.conv2d(gy, kernel_y, padding=(0, 1))

    # Rogner pour avoir la même taille (H, W)
    H, W = x.shape[2:]
    div_x = div_x[:, :, :H, :]
    div_y = div_y[:, :, :, :W]

    return -(div_x + div_y).squeeze()

def gradient_gpu(x):
    grad_x = torch.zeros_like(x)
    grad_y = torch.zeros_like(x)
    grad_x[:-1, :] = x[1:, :] - x[:-1, :]
    grad_y[:, :-1] = x[:, 1:] - x[:, :-1]
    return torch.stack((grad_x, grad_y), dim=0)

def div_gpu(x):
    if x.dim() == 3:
        x = x.unsqueeze(0)  # Devient [1, 2, H, W]
    gx = x[:, 0:1, :, :]  # gradient horizontal
    gy = x[:, 1:2, :, :]  # gradient vertical

    # Définition des noyaux de divergence
    kernel_x = torch.tensor([[[[1.0], [-1.0]]]], dtype=torch.float32, device=x.device)
    kernel_y = torch.tensor([[[[1.0, -1.0]]]], dtype=torch.float32, device=x.device)

    # Appliquer la convolution
    div_x = F.conv2d(gx, kernel_x, padding=(1, 0))
    div_y = F.conv2d(gy, kernel_y, padding=(0, 1))

    # Rogner pour avoir la même taille (H, W)
    H, W = x.shape[2:]
    div_x = div_x[:, :, :H, :]
    div_y = div_y[:, :, :, :W]

    return -(div_x + div_y).squeeze()

def KL_divergence(Ax, y):
    return torch.sum(Ax - y * torch.log(Ax + 1e-10))

def gradient_KL(Ax, y):
    return 1 - y / (Ax + 1e-10)