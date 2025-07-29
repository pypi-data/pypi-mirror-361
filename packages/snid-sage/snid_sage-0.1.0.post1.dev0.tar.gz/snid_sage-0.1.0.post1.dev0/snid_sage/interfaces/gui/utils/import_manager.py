"""
SNID SAGE - Import Manager
==========================

Handles lazy imports and optional dependencies for the SNID SAGE GUI.
Moved from sage_gui.py to reduce main file complexity.

Part of the SNID SAGE GUI restructuring - Utils Module
"""

import tkinter as tk
from tkinter import messagebox

# Import the centralized logging system
try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('gui.import_manager')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('gui.import_manager')

# Import state tracking
_matplotlib_imported = False
_preprocessing_imported = False
_pil_imported = False
_astropy_imported = False
_scipy_imported = False
_snid_dependencies_imported = False


def _import_matplotlib():
    """Lazy import of matplotlib to speed up startup"""
    global _matplotlib_imported
    if not _matplotlib_imported:
        import matplotlib
        matplotlib.use('TkAgg', force=True)  # Force TkAgg backend
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
        import numpy as np
        
        # Configure matplotlib to prevent external windows
        plt.ioff()  # Turn off interactive plotting
        
        # Configure matplotlib to stay embedded
        import matplotlib as mpl
        mpl.rcParams['figure.raise_window'] = False
        mpl.rcParams['tk.window_focus'] = False
        
        # Close any existing figures to prevent conflicts
        plt.close('all')
        
        globals()['plt'] = plt
        globals()['FigureCanvasTkAgg'] = FigureCanvasTkAgg 
        globals()['NavigationToolbar2Tk'] = NavigationToolbar2Tk
        globals()['np'] = np
        _matplotlib_imported = True
        
        
def _import_preprocessing():
    """Lazy import of preprocessing components"""
    global _preprocessing_imported
    if not _preprocessing_imported:
        try:
            from snid_sage.interfaces.gui.preprocessing_gui import SpectrumPreprocessor, PreprocessingDialog
            globals()['SpectrumPreprocessor'] = SpectrumPreprocessor
            globals()['PreprocessingDialog'] = PreprocessingDialog
            _preprocessing_imported = True
            _LOGGER.info("✅ Preprocessing components imported successfully")
        except ImportError as e:
            _LOGGER.warning(f"⚠️ Warning: Could not import preprocessing components: {e}")
            # Create dummy classes to prevent crashes
            class DummySpectrumPreprocessor:
                def __init__(self, parent):
                    self.parent = parent
                    self.original_wave = None
                    self.original_flux = None
                    self.current_wave = None
                    self.current_flux = None
                    self.step_history = []
                def load_spectrum(self, file_path):
                    _LOGGER.warning(f"⚠️ Preprocessing not available - dummy load for {file_path}")
                    return False
            
            class DummyPreprocessingDialog:
                def __init__(self, parent, preprocessor):
                    pass
                def show(self):
                    messagebox.showwarning("Preprocessing Unavailable", 
                                         "Preprocessing features are not available.\n"
                                         "Some dependencies may be missing.")
            
            globals()['SpectrumPreprocessor'] = DummySpectrumPreprocessor
            globals()['PreprocessingDialog'] = DummyPreprocessingDialog
            _preprocessing_imported = True
    

def _import_pil():
    """Lazy import of PIL"""
    global _pil_imported
    if not _pil_imported:
        from PIL import Image, ImageTk
        globals()['Image'] = Image
        globals()['ImageTk'] = ImageTk
        _pil_imported = True


def _import_astropy():
    """Lazy import of astropy"""
    global _astropy_imported
    if not _astropy_imported:
        try:
            import astropy
            from astropy.io import fits
            globals()['astropy'] = astropy
            globals()['fits'] = fits
            _astropy_imported = True
            _LOGGER.info("✅ Astropy imported successfully")
        except ImportError as e:
            _LOGGER.warning(f"⚠️ Warning: Could not import astropy: {e}")
            # Create dummy to prevent crashes
            class DummyFits:
                def open(self, *args, **kwargs):
                    raise ImportError("Astropy not available")
            globals()['fits'] = DummyFits()
            _astropy_imported = True


def _import_scipy():
    """Lazy import of scipy"""
    global _scipy_imported
    if not _scipy_imported:
        try:
            import scipy
            from scipy import signal, interpolate, ndimage
            globals()['scipy'] = scipy
            globals()['signal'] = signal
            globals()['interpolate'] = interpolate
            globals()['ndimage'] = ndimage
            _scipy_imported = True
            _LOGGER.info("✅ Scipy imported successfully")
        except ImportError as e:
            _LOGGER.warning(f"⚠️ Warning: Could not import scipy: {e}")
            _scipy_imported = True


def _import_snid_dependencies():
    """Import core SNID dependencies"""
    global _snid_dependencies_imported
    if not _snid_dependencies_imported:
        try:
            from snid_sage.snid.snid import run_snid, preprocess_spectrum, run_snid_analysis
            globals()['run_snid'] = run_snid
            globals()['preprocess_spectrum'] = preprocess_spectrum
            globals()['run_snid_analysis'] = run_snid_analysis
            _snid_dependencies_imported = True
            _LOGGER.info("✅ SNID dependencies imported successfully")
        except ImportError as e:
            _LOGGER.warning(f"⚠️ Warning: Could not import SNID dependencies: {e}")
            _snid_dependencies_imported = True


def _import_optional_features():
    """Import optional features that might not be available"""
    optional_features = {}
    
    try:
        from snid_sage.shared.utils.line_detection.spectrum_utils import plot_spectrum, apply_savgol_filter
        optional_features['spectrum_utils'] = True
    except ImportError:
        optional_features['spectrum_utils'] = False
    
    try:
        from snid_sage.interfaces.llm.openrouter.openrouter_llm import get_openrouter_config
        optional_features['openrouter'] = True
        optional_features['openrouter_config'] = get_openrouter_config()
    except ImportError:
        optional_features['openrouter'] = False
        optional_features['openrouter_config'] = {}
    
    try:
        from snid_sage.interfaces.llm.local.gpu_llama import LLAMA_AVAILABLE
        optional_features['llama'] = LLAMA_AVAILABLE
    except ImportError:
        optional_features['llama'] = False
    
    return optional_features


def is_matplotlib_imported():
    """Check if matplotlib has been imported"""
    return _matplotlib_imported


def is_preprocessing_imported():
    """Check if preprocessing has been imported"""
    return _preprocessing_imported


def is_pil_imported():
    """Check if PIL has been imported"""
    return _pil_imported


def get_matplotlib_components():
    """Get matplotlib components (import if needed)"""
    if not _matplotlib_imported:
        _import_matplotlib()
    
    return {
        'plt': globals().get('plt'),
        'FigureCanvasTkAgg': globals().get('FigureCanvasTkAgg'),
        'NavigationToolbar2Tk': globals().get('NavigationToolbar2Tk'),
        'np': globals().get('np')
    }


def get_preprocessing_components():
    """Get preprocessing components (import if needed)"""
    if not _preprocessing_imported:
        _import_preprocessing()
    
    return {
        'SpectrumPreprocessor': globals().get('SpectrumPreprocessor'),
        'PreprocessingDialog': globals().get('PreprocessingDialog')
    }


def get_pil_components():
    """Get PIL components (import if needed)"""
    if not _pil_imported:
        _import_pil()
    
    return {
        'Image': globals().get('Image'),
        'ImageTk': globals().get('ImageTk')
    } 
