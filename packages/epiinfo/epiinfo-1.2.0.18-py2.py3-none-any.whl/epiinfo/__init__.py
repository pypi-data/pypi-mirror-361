"""
EpiInfo Python Package

A Python package for epidemiological data analysis and statistical computations.
"""

__version__ = "1.0.0"
__author__ = "EpiInfo Team"

# Import main modules for easier access
from .Frequencies import *
from .Means import *
from .TablesAnalysis import *
from .LinearRegression import *
from .LogisticRegression import *
from .LogBinomialRegression import *
from .ImportData import *
from .LineList import *
from .MakeSQLite import *

# Make commonly used utilities available at package level
from .CSUtilities import *
from .RegressionUtilities import *
from .ResultsFormatting import *

__all__ = [
    # Core analysis modules
    'Frequencies',
    'Means', 
    'TablesAnalysis',
    'LinearRegression',
    'LogisticRegression',
    'LogBinomialRegression',
    
    # Data handling
    'ImportData',
    'LineList',
    'MakeSQLite',
    
    # Utilities
    'CSUtilities',
    'RegressionUtilities', 
    'ResultsFormatting',
    'BigDouble',
    'EICSMeans',
    'EICSTables',
    'EncryptionDecryptionKeys',
    'randata'
]
