import os
import numpy as np

import SVAR.SVARutilGMM
import SVAR.estSVAR
import SVAR.SVARbasics
import pickle
import pytest

import SVAR.estimatorGMM
import SVAR.estimatorGMMW
import SVAR.SVARutil

np.random.seed(0)

if False:
    with open("tests\data\eps.data", 'rb') as filehandle:
        # read the data as binary data stream
        eps = pickle.load(filehandle)
    supply_eps = eps


#
# # path = os.path.join("MCResults", version)
# file_name = "W.data"
# with open(file_name, 'wb') as filehandle:
#     pickle.dump(grad, filehandle)


@pytest.fixture
def supply_eps():
    with open("data/eps.data", 'rb') as filehandle:
        # read the data as binary data stream
        eps = pickle.load(filehandle)
    return eps


@pytest.fixture
def supply_g():
    with open("data/g.data", 'rb') as filehandle:
        # read the data as binary data stream
        g = pickle.load(filehandle)
    return g


# @pytest.fixture
# def supply_W():
#     with open("data/W.data", 'rb') as filehandle:
#         # read the data as binary data stream
#         W = pickle.load(filehandle)
#     return W


@pytest.fixture
def supply_Jac():
    with open("data/Jac.data", 'rb') as filehandle:
        # read the data as binary data stream
        Jac = pickle.load(filehandle)
    return Jac


@pytest.fixture
def supply_grad():
    with open("data/grad.data", 'rb') as filehandle:
        # read the data as binary data stream
        grad = pickle.load(filehandle)
    return grad


@pytest.mark.parametrize("r,n,expected", [
    (3, 2, np.array([[1, 2], [2, 1]])),
    (2, 3, np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]])),
    (3, 3, np.array([[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0], [1, 1, 1]])),
    (4, 3, np.array([[0, 1, 3], [0, 3, 1], [1, 0, 3], [1, 3, 0], [3, 0, 1], [3, 1, 0], [0, 2, 2],
                     [2, 0, 2], [2, 2, 0], [1, 1, 2], [1, 2, 1], [2, 1, 1]]))
])
def test_get_Cr(r, n, expected):
    assert SVAR.SVARutilGMM.get_Cr(r, n).tolist() == expected.tolist()


@pytest.mark.parametrize("r,n,expected", [
    (3, 2, np.array([[3, 0], [0, 3]])),
    (2, 3, np.array([[2, 0, 0], [0, 2, 0], [0, 0, 2]]))
])
def test_get_Mr(r, n, expected):
    assert SVAR.SVARutilGMM.get_Mr(r, n).tolist() == expected.tolist()


@pytest.mark.parametrize("moments,expected", [
    (SVAR.SVARutilGMM.get_Cr(3, 2), np.array([[False, True, False, False, False, False, False, True, False,
                                               False],
                                              [False, False, True, False, False, False, True, False, False,
                                         False]])),
    (SVAR.SVARutilGMM.get_Cr(2, 3),
     np.array([[True, False, False, False, False, False, True, False, False,
                False, False, True, False, False, False],
               [False, True, False, False, False, True, False, False, False,
                False, False, True, False, False, False],
               [False, True, False, False, False, False, True, False, False,
                False, True, False, False, False, False]])),
    (SVAR.SVARutilGMM.get_Cr(3, 3),
     np.array([[True, False, False, False, False, False, True, False, False,
                False, False, False, True, False, False],
               [True, False, False, False, False, False, False, True, False,
                False, False, True, False, False, False],
               [False, True, False, False, False, True, False, False, False,
                False, False, False, True, False, False],
               [False, True, False, False, False, False, False, True, False,
                False, True, False, False, False, False],
               [False, False, True, False, False, True, False, False, False,
                False, False, True, False, False, False],
               [False, False, True, False, False, False, True, False, False,
                False, True, False, False, False, False],
               [False, True, False, False, False, False, True, False, False,
                False, False, True, False, False, False]])),
    (SVAR.SVARutilGMM.get_Cr(4, 3),
     np.array([[True, False, False, False, False, False, True, False, False,
                False, False, False, False, True, False],
               [True, False, False, False, False, False, False, False, True,
                False, False, True, False, False, False],
               [False, True, False, False, False, True, False, False, False,
                False, False, False, False, True, False],
               [False, True, False, False, False, False, False, False, True,
                False, True, False, False, False, False],
               [False, False, False, True, False, True, False, False, False,
                False, False, True, False, False, False],
               [False, False, False, True, False, False, True, False, False,
                False, True, False, False, False, False],
               [True, False, False, False, False, False, False, True, False,
                False, False, False, True, False, False],
               [False, False, True, False, False, True, False, False, False,
                False, False, False, True, False, False],
               [False, False, True, False, False, False, False, True, False,
                False, True, False, False, False, False],
               [False, True, False, False, False, False, True, False, False,
                False, False, False, True, False, False],
               [False, True, False, False, False, False, False, True, False,
                False, False, True, False, False, False],
               [False, False, True, False, False, False, True, False, False,
                False, False, True, False, False, False]])),
    (SVAR.SVARutilGMM.get_Mr(3, 2), np.array([[False, False, False, True, False, True, False, False, False,
                                               False],
                                              [True, False, False, False, False, False, False, False, True,
                                         False]])),
    (SVAR.SVARutilGMM.get_Mr(2, 3),
     np.array([[False, False, True, False, False, True, False, False, False,
                False, True, False, False, False, False],
               [True, False, False, False, False, False, False, True, False,
                False, True, False, False, False, False],
               [True, False, False, False, False, True, False, False, False,
                False, False, False, True, False, False]])),
])
def test_get_Moments_powerindex(moments, expected):
    assert SVAR.SVARutilGMM.get_Moments_powerindex(moments).tolist() == expected.tolist()


@pytest.mark.parametrize("moment,expected", [
    (SVAR.SVARutilGMM.get_Cr(3, 2)[0], np.array([1, 2, 2])),
    (SVAR.SVARutilGMM.get_Cr(3, 2)[1], np.array([1, 1, 2])),
    (SVAR.SVARutilGMM.get_Cr(3, 3)[0], np.array([2, 3, 3])),
    (SVAR.SVARutilGMM.get_Cr(3, 3)[1], np.array([2, 2, 3])),
    (SVAR.SVARutilGMM.get_Cr(3, 3)[6], np.array([1, 2, 3])),
    (SVAR.SVARutilGMM.get_Cr(4, 3)[0], np.array([2, 3, 3, 3])),
    (SVAR.SVARutilGMM.get_Cr(4, 3)[5], np.array([1, 1, 1, 2])),
    (SVAR.SVARutilGMM.get_Mr(2, 2)[0], np.array([1, 1])),
    (SVAR.SVARutilGMM.get_Mr(2, 2)[1], np.array([2, 2])),
    (SVAR.SVARutilGMM.get_Mr(2, 3)[0], np.array([1, 1])),
    (SVAR.SVARutilGMM.get_Mr(2, 3)[2], np.array([3, 3])),
])
def test_get_Moment_transformed(moment, expected):
    assert SVAR.SVARutilGMM.get_Moment_transformed(moment).tolist() == expected.tolist()


@pytest.mark.parametrize("b,restrictions,whiten,expected", [

    ([1, 2, 3, 4, 5, 6, 7, 8, 9], [], False,
     np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])),

    ([1, 2, 3, 4, 5, 6, 7, 8, 9],
     np.array([[np.nan, np.nan, np.nan], [np.nan, np.nan, np.nan], [np.nan, np.nan, np.nan]]), False,
     np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])),

    ([2, 3, 4, 5, 6, 7, 8, 9],
     np.array([[0, np.nan, np.nan], [np.nan, np.nan, np.nan], [np.nan, np.nan, np.nan]]), False,
     np.array([[0, 2, 3], [4, 5, 6], [7, 8, 9]])),

    ([2, 3, 4, 5, 6, 7, 8, 9],
     np.array([[10, np.nan, np.nan], [np.nan, np.nan, np.nan], [np.nan, np.nan, np.nan]]), False,
     np.array([[10, 2, 3], [4, 5, 6], [7, 8, 9]])),

    ([1, 4, 5, 7, 8, 9],
     SVAR.SVARutil.getRestrictions_recursive(np.array([[1, 0, 0], [4, 5, 0], [7, 8, 9]])), False,
     np.array([[1, 0, 0], [4, 5, 0], [7, 8, 9]])),

    ([np.pi / 2], [], True,
     np.array([[0., -1.], [1., 0.]])),

    ([0, 0, np.pi / 2], [], True,
     np.array([[1., 0., 0.], [0., 0., -1.], [0., 1., 0.]])),
])
def test_get_BMatrix(b, restrictions, whiten, expected):
    assert SVAR.SVARutil.get_BMatrix(b=b, restrictions=restrictions, whiten=whiten).tolist() == expected.tolist()


@pytest.mark.parametrize("B,restrictions,expected", [
    (np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), [], np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])),

    (np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
     np.array([[np.nan, np.nan, np.nan], [np.nan, np.nan, np.nan], [np.nan, np.nan, np.nan]]),
     np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])),

    (np.array([[0, 2, 3], [4, 5, 6], [7, 8, 9]]),
     np.array([[0, np.nan, np.nan], [np.nan, np.nan, np.nan], [np.nan, np.nan, np.nan]]),
     np.array([2, 3, 4, 5, 6, 7, 8, 9])),

    (np.array([[10, 2, 3], [4, 5, 6], [7, 8, 9]]),
     np.array([[10, np.nan, np.nan], [np.nan, np.nan, np.nan], [np.nan, np.nan, np.nan]]),
     np.array([2, 3, 4, 5, 6, 7, 8, 9])),

    (np.array([[1, 0, 0], [4, 5, 0], [7, 8, 9]]),
     SVAR.SVARutil.getRestrictions_recursive(np.array([[1, 0, 0], [4, 5, 0], [7, 8, 9]])),
     np.array([1, 4, 5, 7, 8, 9]))
])
def test_get_bVector(B, restrictions, expected):
    assert SVAR.SVARutil.get_BVector(B=B, restrictions=restrictions).tolist() == expected.tolist()


def test_get_Omega():
    # eps = supply_eps[:,:2]
    eps = np.array([[2, 3], [2, 3]])
    Omega2, Omega3, Omega4 = SVAR.SVARutil.get_Omega(eps)
    Omega2_exp = np.array([[4., 6.], [np.nan, 9.]])
    Omega3_exp = np.array([[[8., 12.],
                            [np.nan, 18.]],
                           [[np.nan, np.nan],
                            [np.nan, 27.]]])
    Omega4_exp = np.array([[[[16., 24.],
                             [np.nan, 36.]],
                            [[np.nan, np.nan],
                             [np.nan, 54.]]],
                           [[[np.nan, np.nan],
                             [np.nan, np.nan]],
                            [[np.nan, np.nan],
                             [np.nan, 81.]]]])
    assert Omega2[~np.isnan(Omega2)].tolist() == Omega2_exp[~np.isnan(Omega2)].tolist()
    assert Omega3[~np.isnan(Omega3)].tolist() == Omega3_exp[~np.isnan(Omega3)].tolist()
    assert Omega4[~np.isnan(Omega4)].tolist() == Omega4_exp[~np.isnan(Omega4)].tolist()

    assert Omega2[~np.isnan(Omega2_exp)].tolist() == Omega2_exp[~np.isnan(Omega2_exp)].tolist()
    assert Omega3[~np.isnan(Omega3_exp)].tolist() == Omega3_exp[~np.isnan(Omega3_exp)].tolist()
    assert Omega4[~np.isnan(Omega4_exp)].tolist() == Omega4_exp[~np.isnan(Omega4_exp)].tolist()


def test_get_f():
    u = np.array([[2, 3], [2, 3] ])
    b = np.array([1, 0, 0, 1])
    restrictions = []
    n = 2
    moments = SVAR.SVARutilGMM.get_Mr(2, n)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Cr(2, n), axis=0)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Cr(3, n), axis=0)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Cr(4, n), axis=0)
    moments_powerindex = SVAR.SVARutilGMM.get_Moments_powerindex(moments)
    whiten = False
    f = SVAR.SVARutilGMM.get_f(u, b, restrictions, moments, moments_powerindex, whiten=whiten)
    expected = np.array([[3., 8., 6., 18., 12., 54., 24., 35.],
                         [3., 8., 6., 18., 12., 54., 24., 35.]])
    assert f.tolist() == expected.tolist()

    u = np.array([[2, 3], [2, 3]])
    b = np.array([0])
    restrictions = []
    n = 2
    moments = SVAR.SVARutilGMM.get_Mr(3, n)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Mr(4, n), axis=0)
    moments_powerindex = SVAR.SVARutilGMM.get_Moments_powerindex(moments)
    whiten = True
    f = SVAR.SVARutilGMM.get_f(u, b, restrictions, moments, moments_powerindex, whiten=whiten)
    expected = np.array([[8., 27., 13., 78.],
                         [8., 27., 13., 78.]])
    assert f.tolist() == expected.tolist()


def test_get_g(supply_eps, supply_g):
    n = 5
    u = supply_eps[:, :n]
    restrictions = []
    B = np.eye(n)
    b = SVAR.SVARutil.get_BVector(B, restrictions=restrictions)
    moments = SVAR.SVARutilGMM.get_Mr(2, n)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Cr(2, n), axis=0)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Cr(3, n), axis=0)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Cr(4, n), axis=0)
    moments_powerindex = SVAR.SVARutilGMM.get_Moments_powerindex(moments)
    whiten = False
    g = SVAR.SVARutilGMM.get_g(u, b, restrictions, moments, moments_powerindex, whiten)
    assert g.tolist() == supply_g.tolist()

    moments = SVAR.SVARutilGMM.get_Mr(3, n)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Mr(4, n), axis=0)
    moments_powerindex = SVAR.SVARutilGMM.get_Moments_powerindex(moments)
    whiten = True
    b = SVAR.SVARutil.get_BVector(B, whiten=whiten)
    g = SVAR.SVARutilGMM.get_g(u, b, restrictions, moments, moments_powerindex, whiten)
    gnew = SVAR.SVARutilGMM.get_g_wf(u, b, restrictions, moments, moments_powerindex, whiten)

    g=np.round(g,5)
    gnew=np.round(gnew, 5)

    assert g.tolist() == gnew.tolist()

    moments= SVAR.SVARutilGMM.get_Moments_MIcorrection(n, blocks=False)
    moments_powerindex = SVAR.SVARutilGMM.get_Moments_powerindex(moments)
    g1 = SVAR.SVARutilGMM.get_g_wf(b=b, u=u, restrictions=restrictions, moments=moments, moments_powerindex=moments_powerindex,
          whiten=whiten, blocks=False )
    g2 = SVAR.SVARutilGMM.get_g(b=b, u=u, restrictions=restrictions, moments=moments, moments_powerindex=moments_powerindex,
          whiten=whiten, blocks=False  )

    g1=np.round(g1,5)
    g2=np.round(g2, 5)

    assert g1.tolist() == g2.tolist()


def test_loss():
    u = np.array([[2, 3], [2, 3]])
    b = np.array([1, 0, 0, 1])
    restrictions = []
    n = 2
    moments = SVAR.SVARutilGMM.get_Mr(2, n)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Cr(2, n), axis=0)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Cr(3, n), axis=0)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Cr(4, n), axis=0)
    moments_powerindex = SVAR.SVARutilGMM.get_Moments_powerindex(moments)
    whiten = False
    g = SVAR.SVARutilGMM.get_g(u, b, restrictions, moments, moments_powerindex, whiten)
    W = np.eye(np.shape(moments)[0])
    loss = SVAR.estimatorGMM.loss(u, b, W=W, moments=moments, moments_powerindex=moments_powerindex, restrictions=restrictions)
    assert loss == 5294.0




def test_get_W_optimal(supply_eps):
    n = 2
    u = supply_eps[:, :n]
    restrictions = []
    B = np.eye(n)
    b = SVAR.SVARutil.get_BVector(B, restrictions=restrictions)
    moments = SVAR.SVARutilGMM.get_Mr(2, n)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Cr(2, n), axis=0)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Cr(3, n), axis=0)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Cr(4, n), axis=0)
    moments_powerindex = SVAR.SVARutilGMM.get_Moments_powerindex(moments)

    W = SVAR.SVARutilGMM.get_W_opt(u, b, restrictions, moments, Wpara='Uncorrelated')


    f = SVAR.SVARutilGMM.get_f(u=u, b=b, restrictions=restrictions, moments=moments,
              moments_powerindex=moments_powerindex)
    S = np.cov(f.T )
    W_expected = np.linalg.inv(S)

    assert W.tolist() == W_expected.tolist()

    W = SVAR.SVARutilGMM.get_W_opt(u, b, restrictions, moments, Wpara='Independent')

    e = SVAR.innovation(u, b, restrictions=restrictions)
    omega = SVAR.SVARutil.get_Omega_Moments(e)
    S = SVAR.SVARutilGMM.get_S_Indep(Moments_1=moments, Moments_2=moments, omega=omega)
    W_expected = np.linalg.inv(S)


    assert W.tolist() == W_expected.tolist()

def test_Jacobian(supply_eps, supply_Jac):
    n = 5
    u = supply_eps[:, :n]
    restrictions = np.full([n, n], np.nan)
    B = np.eye(n)
    b = SVAR.SVARutil.get_BVector(B, restrictions=restrictions)
    moments = SVAR.SVARutilGMM.get_Mr(2, n)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Cr(2, n), axis=0)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Cr(3, n), axis=0)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Cr(4, n), axis=0)
    moments_powerindex = SVAR.SVARutilGMM.get_Moments_powerindex(moments)

    Jacobian = SVAR.SVARutilGMM.generate_Jacobian_function(moments=moments, restrictions=restrictions)
    Omega = SVAR.SVARutil.get_CoOmega(supply_eps)
    Jac = Jacobian(u=u, b=b, restrictions=restrictions, CoOmega=Omega)

    Jac=np.round(Jac,5)
    supply_Jac=np.round(supply_Jac,5)

    assert Jac.tolist() == supply_Jac.tolist()


def test_gradient(supply_eps):
    n = 5
    u = supply_eps[:, :n]
    restrictions = np.full([n, n], np.nan)
    B = np.eye(n)
    b = SVAR.SVARutil.get_BVector(B, restrictions=restrictions)
    moments = SVAR.SVARutilGMM.get_Mr(2, n)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Cr(2, n), axis=0)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Cr(3, n), axis=0)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Cr(4, n), axis=0)
    moments_powerindex = SVAR.SVARutilGMM.get_Moments_powerindex(moments)
    whiten = False
    W = SVAR.SVARutilGMM.get_W_opt(u, b, restrictions, moments, Wpara='Uncorrelated')
    Jacobian = SVAR.SVARutilGMM.generate_Jacobian_function(moments=moments, restrictions=restrictions)
    grad = SVAR.estimatorGMM.gradient(u, b, Jacobian, W, restrictions, moments, moments_powerindex)
    grad = np.round(grad,8)
    grad_expected = np.array([0.04618893, -0.04448169, -0.03513598, 0.05428982, 0.06848366, -0.03515186, 0.05826086, 0.0833233, 0.06300775, 0.02590376, 0.01839882, 0.04160729, 0.09385199, -0.03826313, -0.00118679, 0.05079445, 0.08096382, -0.06218975, 0.02402831, -0.08431825, -0.02568715, 0.06836932, 0.00219649, -0.08167082, 0.07344885])

    assert grad.tolist() == grad_expected.tolist()




def test_fast_weighting(supply_eps):
    n = 4
    u = supply_eps[:, :n]

    def check_fast_weighting(b):
        # GMM_W with Wfast
        # block1 = np.array([1, 2])
        # block2 = np.array([3, 4])
        # blocks = list()
        # blocks.append(block1)
        # blocks.append(block2)
        # moments = SVAR.K_GMM.get_Moments('GMM_W', n, blocks=blocks)
        # moments_powerindex = SVAR.K_GMM.get_Moments_powerindex(moments)
        # W = SVAR.K_GMM.get_W_fast(moments)
        # J2 = SVAR.K_GMM.loss(u, b, W, restrictions=[], moments=moments, moments_powerindex=moments_powerindex, whiten=True, blocks=False)
        # #print('J2:', J2)

        # GMM_W with Wfast
        moments = SVAR.SVARutilGMM.get_Cr(4, 4)
        moments_powerindex = SVAR.SVARutilGMM.get_Moments_powerindex(moments)
        W = SVAR.estimatorGMMW.get_W_fast(moments)
        J = SVAR.estimatorGMMW.loss(u, b, W, restrictions=[], moments=moments, moments_powerindex=moments_powerindex,
                                     blocks=False)
        # print('J:', J)

        # GMM fast
        moments = SVAR.SVARutilGMM.get_Mr(4, 4)
        moments_powerindex = SVAR.SVARutilGMM.get_Moments_powerindex(moments)
        W = np.eye(np.shape(moments)[0])
        H = SVAR.estimatorGMMW.loss(u, b, W, restrictions=[], moments=moments, moments_powerindex=moments_powerindex,
                                      blocks=False)
        # print('H:', H)

        # print('J+H',J+H)
        # print('J2+H',J2+H)
        # print(" ")
        return J, H

    b = np.array([1., 0, 0., 0., 0., 0.])
    J1, H1 = check_fast_weighting(b)

    b = np.array([0., 1, 0., 0., 0., 0.])
    J2, H2 = check_fast_weighting(b)

    b = np.array([0., 1, 1., 1., 0., 1.])
    J3, H3 = check_fast_weighting(b)

    assert np.round(J1 + H1,5) == np.round(J2 + H2,5)
    assert np.round(J1 + H1,5) == np.round(J3 + H3,5)
    assert np.round(J2 + H2,5) == np.round(J3 + H3,5)
