from molscore.scoring_functions.glide import GlideDock
from molscore.scoring_functions.plants import PLANTSDock
from molscore.scoring_functions.gold import GOLDDock, ChemPLPGOLDDock, ASPGOLDDock, ChemScoreGOLDDock, GoldScoreGOLDDock
from molscore.scoring_functions.rdock import rDock
from molscore.scoring_functions.smina import SminaDock
from molscore.scoring_functions.vina import VinaDock
from molscore.scoring_functions.similarity import MolecularSimilarity, TanimotoSimilarity
from molscore.scoring_functions.applicability_domain import ApplicabilityDomain
from molscore.scoring_functions.external_server import POSTServer
from molscore.scoring_functions.align3d import Align3D
from molscore.scoring_functions.pidgin import PIDGIN
from molscore.scoring_functions.descriptors import MolecularDescriptors, RDKitDescriptors
from molscore.scoring_functions.isomer import Isomer
from molscore.scoring_functions.substructure_filters import SubstructureFilters
from molscore.scoring_functions.substructure_match import SubstructureMatch
from molscore.scoring_functions.sklearn_model import SKLearnModel, EnsembleSKLearnModel, SKLearnClassifier, SKLearnRegressor
from molscore.scoring_functions.rascore_xgb import RAScore_XGB
from molscore.scoring_functions.aizynthfinder import AiZynthFinder

all_scoring_functions = [
    MolecularSimilarity, 
    TanimotoSimilarity, # Back compatability
    MolecularDescriptors,
    RDKitDescriptors, # Back compatability
    ApplicabilityDomain,
    Isomer,
    SubstructureFilters,
    SubstructureMatch,
    SKLearnModel,
    EnsembleSKLearnModel,
    POSTServer,
    PIDGIN,
    RAScore_XGB,
    AiZynthFinder,
    Align3D,
    GlideDock,
    SminaDock,
    VinaDock,
    rDock,
    PLANTSDock,
    GOLDDock,
    ChemPLPGOLDDock,
    ASPGOLDDock,
    ChemScoreGOLDDock,
    GoldScoreGOLDDock
]

try:
    from molscore.scoring_functions.rocs import ROCS, GlideDockFromROCS
    from molscore.scoring_functions.oedock import OEDock
    all_scoring_functions += [ROCS, GlideDockFromROCS, OEDock]
except ImportError:
    pass # print("To use openeye scoring functions please install openeye and acquire a license")

try:
    from molscore.scoring_functions.chemprop import ChemPropModel
    all_scoring_functions += [ChemPropModel]
except ImportError:
    pass # print("To use ChemProp please install the relevant version of PyTorch and ChemProp")

# ----- To load the classical DRD2 test case requires an old version of Scikit-learn
#from molscore.scoring_functions.reinvent_svm import ActivityModel
#all_scoring_functions += [ActivityModel]
