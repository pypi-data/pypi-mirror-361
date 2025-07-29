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




def test_GMM_avar(supply_eps):
    n = 2
    u = supply_eps[:, :n]
    restrictions = np.full([n, n], np.nan)
    B = np.eye(n)
    b = SVAR.SVARutil.get_BVector(B, restrictions=restrictions)
    moments = SVAR.SVARutilGMM.get_Mr(2, n)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Cr(2, n), axis=0)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Cr(3, n), axis=0)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Cr(4, n), axis=0)
    W = np.eye(np.shape(moments)[0])
    k_step = 1
    # GMM_out = SVAR.K_GMM.GMM(u, b, Jacobian, W, restrictions, moments, kstep=k_step)
    opt_svar = dict()
    opt_svar['W'] = W
    opt_svar['Wstartopt'] = 'specific'
    opt_svar['kstep'] = k_step
    opt_svar['bstartopt'] = 'specific'
    opt_svar['bstart'] = b
    opt_svar['moments'] = moments
    opt_svar['restrictions'] = restrictions
    opt_svar['Avarparametric'] = "Independent"
    opt_svar['WupdateInOutput'] = False


    svar_out = SVAR.SVARest(u, estimator='GMM', prepOptions=opt_svar)
    V = svar_out['Avar_est']
    V_expected = np.array([[1.9402818468659488, 0.2733512070290248, 0.1284802727181451, 0.7012494706027909], [0.2733512070290248, 1.9756584345286183, -0.8135648505469544, 0.08800376364855292], [0.12848027271814508, -0.8135648505469546, 2.0956674150027013, 0.31668421313059375], [0.7012494706027907, 0.08800376364855292, 0.31668421313059375, 1.968376039877903]])

    V = np.round(V, 5)
    V_expected = np.round(V_expected, 5)

    assert V.tolist()  == V_expected.tolist()

    opt_svar['Avarparametric'] = "Uncorrelated"
    svar_out = SVAR.SVARest(u, estimator='GMM', prepOptions=opt_svar)
    V = svar_out['Avar_est']
    V_expected = np.array([[1.7409070057869636, -0.0317006809061288, 0.15592176107093303, 0.46321910091505997], [-0.03170068090612883, 1.4952798978427135, -0.6335438399532474, -0.3004910762201573], [0.155921761070933, -0.6335438399532474, 1.7048115431668374, 0.3879469041436635], [0.46321910091505986, -0.3004910762201573, 0.3879469041436635, 1.6913747391778382]])

    V = np.round(V, 5)
    V_expected = np.round(V_expected, 5)

    assert V.tolist() == V_expected.tolist()



def test_GMM(supply_eps):
    n = 2
    u = supply_eps[:, :n]
    restrictions = np.full([n, n], np.nan)
    B = np.eye(n)
    b = SVAR.SVARutil.get_BVector(B, restrictions=restrictions)
    moments = SVAR.SVARutilGMM.get_Mr(2, n)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Cr(2, n), axis=0)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Cr(3, n), axis=0)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Cr(4, n), axis=0)
    W = np.eye(np.shape(moments)[0])
    k_step = 1
    # GMM_out = SVAR.K_GMM.GMM(u, b, Jacobian, W, restrictions, moments, kstep=k_step)
    prepOptions = dict()
    prepOptions['W'] = W
    prepOptions['Wstartopt'] = 'specific'
    prepOptions['kstep'] = k_step
    prepOptions['bstartopt'] = 'specific'
    prepOptions['bstart'] = b
    prepOptions['moments'] = moments
    prepOptions['restrictions'] = restrictions
    prepOptions['Avarparametric'] = "Independent"
    svar_out = SVAR.SVARest(u, estimator='GMM', prepOptions=prepOptions)
    B_est = svar_out['B_est']
    loss = svar_out['loss']
    avar = svar_out['Avar_est']

    avar_expected = np.array([[1.9402818468659488, 0.2733512070290248, 0.1284802727181451, 0.7012494706027909], [0.2733512070290248, 1.9756584345286183, -0.8135648505469544, 0.08800376364855292], [0.12848027271814508, -0.8135648505469546, 2.0956674150027013, 0.31668421313059375], [0.7012494706027907, 0.08800376364855292, 0.31668421313059375, 1.968376039877903]])
    loss_expected = 0.0010397156643544272
    B_est_expected = np.array([[0.9935424993853278, -0.008754219586363085], [0.010958149691157675, 1.0134172158135832]])

    loss = np.round(loss, 5)
    loss_expected = np.round(loss_expected, 5)
    B_est = np.round(B_est, 5)
    B_est_expected = np.round(B_est_expected, 5)
    avar = np.round(avar, 5)
    avar_expected = np.round(avar_expected, 5)

    assert loss == loss_expected
    assert svar_out['options']['bstart'].tolist() == b.tolist()
    assert svar_out['options']['moments'].tolist() == moments.tolist()
    assert svar_out['options']['kstep'] == k_step
    assert B_est.tolist() == B_est_expected.tolist()
    assert svar_out['options']['W'].tolist() == W.tolist()
    assert avar.tolist() == avar_expected.tolist()

    prepOptions = dict()
    prepOptions['Wstartopt'] = 'I'
    svar_out = SVAR.SVARest(u, estimator='GMM', prepOptions=prepOptions)
    B_est = svar_out['B_est']
    loss = svar_out['loss']
    loss_expected = 0.0005985534575471171
    B_est_expected = np.array([[0.99407, -0.00511], [0.01775, 1.01315]])

    loss = np.round(loss, 5)
    loss_expected = np.round(loss_expected, 5)
    B_est = np.round(B_est, 5)
    B_est_expected = np.round(B_est_expected, 5)

    assert loss == loss_expected
    assert B_est.tolist() == B_est_expected.tolist()

    prepOptions = dict()
    prepOptions['bstartopt'] = 'GMM_WF'
    prepOptions['Wstartopt'] = 'WoptBstart'
    prepOptions['kstep'] = 1
    svar_out = SVAR.SVARest(u, estimator='GMM', prepOptions=prepOptions)
    B_est = svar_out['B_est']
    loss = svar_out['loss']
    loss_expected = 0.0006255099149225711
    B_est_expected = np.array([[0.99367, -0.0051], [0.01749, 1.01291]])

    loss = np.round(loss, 5)
    loss_expected = np.round(loss_expected, 5)
    B_est = np.round(B_est, 5)
    B_est_expected = np.round(B_est_expected, 5)


    assert loss == loss_expected
    assert B_est.tolist() == B_est_expected.tolist()

    prepOptions = dict()
    prepOptions['bstartopt'] = 'I'
    prepOptions['Wstartopt'] = 'WoptBstart'
    prepOptions['kstep'] = 1
    svar_out = SVAR.SVARest(u, estimator='GMM', prepOptions=prepOptions)
    B_est = svar_out['B_est']
    loss = svar_out['loss']
    loss_expected = 0.0005942712186022502
    B_est_expected = np.array([[0.9944162541003781, -0.004656693154018139], [0.01728797491300107, 1.0129375965423226]])

    loss = np.round(loss, 5)
    loss_expected = np.round(loss_expected, 5)
    B_est = np.round(B_est, 5)
    B_est_expected = np.round(B_est_expected, 5)

    assert loss == loss_expected
    assert B_est.tolist() == B_est_expected.tolist()


def test_GMM_white(supply_eps):
    n = 2
    u = supply_eps[:, :n]
    b = np.array([0])
    moments = SVAR.SVARutilGMM.get_Cr(3, n)
    moments = np.append(moments, SVAR.SVARutilGMM.get_Cr(4, n), axis=0)
    W = np.eye(np.shape(moments)[0])

    prepOptions = dict()
    prepOptions['W'] = W
    prepOptions['Wstartopt'] = 'specific'
    prepOptions['bstart'] = b
    prepOptions['bstartopt'] = 'specific'
    prepOptions['moments'] = moments
    svar_out = SVAR.SVARest(u, estimator='GMM_W', prepOptions=prepOptions)
    B_est = svar_out['B_est']
    loss = svar_out['loss']
    Omega2 = svar_out['Omega_all'][0]
    Omega2 = np.round(Omega2, 15)


    loss_expected = 0.003865450152482355
    B_est_expected = np.array([[0.997230283623227, -0.004399373906083158], [0.014447338782992897, 1.017457148695816]])
    Omega2_expected = np.array([[1.0, -0.0], [np.nan, 1.0]])

    loss = np.round(loss, 5)
    loss_expected = np.round(loss_expected, 5)
    B_est = np.round(B_est, 5)
    B_est_expected = np.round(B_est_expected, 5)
    Omega2 = np.round(Omega2, 5)
    Omega2_expected = np.round(Omega2_expected, 5)

    assert loss == loss_expected
    assert B_est.tolist() == B_est_expected.tolist()
    assert Omega2[~np.isnan(Omega2)].tolist() == Omega2_expected[~np.isnan(Omega2)].tolist()

def test_GMM_fast(supply_eps):
    n = 2
    u = supply_eps[:, :n]
    b = np.array([0])

    prepOptions = dict()
    prepOptions['bstart'] = b
    prepOptions['bstartopt'] = 'specific'
    svar_out = SVAR.SVARest(u, estimator='GMM_WF', prepOptions=prepOptions)
    B_est = svar_out['B_est']
    loss = svar_out['loss']
    Omega2 = svar_out['Omega_all'][0]
    Omega2 = np.round(Omega2, 15)

    loss_expected = -19.7494828332592
    B_est_expected = np.array([[0.997231567472602, -0.004098036379113462], [0.014139888759238346, 1.0174614678581229]])
    Omega2_expected = np.array([[1.0, -0.0], [np.nan, 1.0]])

    loss = np.round(loss, 5)
    loss_expected = np.round(loss_expected, 5)
    B_est = np.round(B_est, 5)
    B_est_expected = np.round(B_est_expected, 5)
    Omega2 = np.round(Omega2, 5)
    Omega2_expected = np.round(Omega2_expected, 5)


    assert loss == loss_expected
    assert B_est.tolist() == B_est_expected.tolist()
    assert Omega2[~np.isnan(Omega2)].tolist() == Omega2_expected[~np.isnan(Omega2)].tolist()

def test_PML(supply_eps):
    n = 2
    u = supply_eps[:, :n]
    b = np.array([0])

    prepOptions = dict()
    prepOptions['bstart'] = b
    prepOptions['bstartopt'] = 'specific'
    svar_out = SVAR.SVARest(u, estimator='PML', prepOptions=prepOptions)
    B_est = svar_out['B_est']
    loss = svar_out['loss']
    Omega2 = svar_out['Omega_all'][0]

    loss_expected = 4257.468466265423
    B_est_expected = np.array([[0.9972396384007051, 0.0008346666749092252], [0.009106998762809449, 1.0175189617907199]])
    Omega2_expected = np.array([[ 1., -0.], [np.nan,  1.]])

    loss = np.round(loss, 5)
    loss_expected = np.round(loss_expected, 5)
    B_est = np.round(B_est, 5)
    B_est_expected = np.round(B_est_expected, 5)
    Omega2 = np.round(Omega2, 5)
    Omega2_expected = np.round(Omega2_expected, 5)


    assert loss == loss_expected
    assert B_est.tolist() == B_est_expected.tolist()
    assert Omega2[~np.isnan(Omega2)].tolist() == Omega2_expected[~np.isnan(Omega2)].tolist()


def test_GMM_PartlyRecurisve(supply_eps):
    n = 5
    u = supply_eps[:, :n]

    n_rec = 2
    prepOptions = dict()
    prepOptions['n_rec'] = n_rec
    prepOptions['Wstartopt'] = 'I'
    SVAR_out = SVAR.SVARest(u, estimator='GMM_W', prepOptions=prepOptions)
    B_est_PC = SVAR_out['B_est']

    prepOptions = dict()
    prepOptions['n_rec'] = 5
    prepOptions['Wstartopt'] = 'I'
    Rec_out = SVAR.SVARest(u, estimator='GMM', prepOptions=prepOptions)
    B_est_rec = Rec_out['B_est']

    B_est_rec = np.round(B_est_rec, 5)
    B_est_PC = np.round(B_est_PC, 5)

    assert B_est_PC[:n_rec,:n_rec].tolist() == B_est_rec[:n_rec,:n_rec].tolist()

    expected = np.array([[0.003330608469677456, -0.033621407028708195],
 [-0.010995613002447795, -0.020220644924939964],
 [-0.0179660316466463, -0.0012376406712120119]])

    B_est_PC = np.round(B_est_PC, 5)
    expected = np.round(expected, 5)

    assert B_est_PC[n_rec:,:n_rec].tolist() == expected.tolist()

    expected = np.array([[0.9845972613833915, 0.02681168147749875, 0.004427083644211701],
 [-0.003259823923889076, 1.001091873682849, 0.00533142301218077],
 [0.0022816522163611945, 0.011374323197186675, 0.988404250711615]])

    B_est_PC = np.round(B_est_PC, 5)
    expected = np.round(expected, 5)

    assert B_est_PC[n_rec:, n_rec:].tolist() == expected.tolist()

    n_rec = 2
    prepOptions = dict()
    prepOptions['n_rec'] = n_rec
    prepOptions['bstartopt'] = 'GMM_WF'
    prepOptions['Wstartopt'] = 'WoptBstart'
    prepOptions['kstep'] = 1
    SVAR_out = SVAR.SVARest(u, estimator='GMM', prepOptions=prepOptions)
    B_est = SVAR_out['B_est']
    B_est_expected = np.array([[0.99661, 0.0, 0.0, 0.0, 0.0],
 [0.01134, 1.01706, 0.0, 0.0, 0.0],
 [0.00259, -0.03242, 0.98471, 0.00436, 0.01147],
 [-0.01471, -0.01624, 0.01191, 0.99008, 0.01359],
 [-0.01949, -0.00042, -0.00574, 0.00885, 0.98538]])

    B_est = np.round(B_est, 5)
    B_est_expected = np.round(B_est_expected, 5)

    assert B_est.tolist() == B_est_expected.tolist()

def test_GMM_BlockRecrusive(supply_eps):
    n = 5
    u = supply_eps[:, :n]

    block1 = np.array([1, 1])
    block2 = np.array([2, 2])
    block3 = np.array([3, 5])
    blocks = list()
    blocks.append(block1)
    blocks.append(block2)
    blocks.append(block3)

    prepOptions = dict()
    prepOptions['blocks'] = blocks
    prepOptions['printOutput'] = False
    SVAR_out = SVAR.SVARest(u, estimator='GMM_WF', prepOptions=prepOptions)
    B_est_PC = SVAR_out['B_est']

    prepOptions = dict()
    prepOptions['n_rec'] = 5
    prepOptions['Wstartopt'] = 'I'
    prepOptions['printOutput'] = False
    Rec_out = SVAR.SVARest(u, estimator='GMM', prepOptions=prepOptions)
    B_est_rec = Rec_out['B_est']

    B_est_rec = np.round(B_est_rec, 5)
    B_est_PC = np.round(B_est_PC, 5)

    assert  B_est_PC[:2,:2].tolist() == B_est_rec[:2,:2].tolist()

    expected = np.array([[0.003330608469677456, -0.033621407028708195],
 [-0.010995613002447795, -0.020220644924939964],
 [-0.0179660316466463, -0.0012376406712120119]] )

    B_est_PC = np.round(B_est_PC, 5)
    expected = np.round(expected, 5)

    assert B_est_PC[2:,:2].tolist() == expected.tolist()

    expected = np.array([[0.9845877900231426, 0.027117178672422547, 0.004666349227279161],
 [-0.003575857115028188, 1.0010856031042032, 0.0062304558880683265],
 [0.0020623518472946143, 0.010486623020412799, 0.988414549383155]])

    B_est_PC = np.round(B_est_PC, 5)
    expected = np.round(expected, 5)

    assert np.round(B_est_PC[2:, 2:],5).tolist() == np.round(expected,5).tolist()










