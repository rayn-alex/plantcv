import pytest
import os
import pickle as pkl
import numpy as np
import matplotlib

# Disable plotting
matplotlib.use("Template")


class TestData:
    def __init__(self):
        """Initialize simple variables."""
        # Test data directory
        self.datadir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testdata")
        # Flat image directory
        self.snapshot_dir = os.path.join(self.datadir, "snapshot_dir")
        # RGB image
        self.small_rgb_img = os.path.join(self.datadir, "setaria_small_plant_rgb.png")
        # Binary mask for RGB image
        self.small_bin_img = os.path.join(self.datadir, "setaria_small_plant_mask.png")
        # Gray image
        self.small_gray_img = os.path.join(self.datadir, "setaria_small_plant_gray.png")
        # Contours file
        self.small_contours_file = os.path.join(self.datadir, "setaria_small_plant_contours.npz")
        # Composed contours file
        self.small_composed_contours_file = os.path.join(self.datadir, "setaria_small_plant_composed_contours.npz")
        # PlantCV Spectral_data object
        self.hsi_file = os.path.join(self.datadir, "hsi.pkl")
        # Binary mask for HSI
        self.hsi_mask_file = os.path.join(self.datadir, "hsi_mask.png")
        # Outputs results file - JSON
        self.outputs_results_json = os.path.join(self.datadir, "outputs_results.json")
        # Outputs results file - CSV
        self.outputs_results_csv = os.path.join(self.datadir, "outputs_results.csv")
        # RGBA image
        # Image from http://www.libpng.org/pub/png/png-OwlAlpha.html
        # This image may be used, edited and reproduced freely.
        self.rgba_img = os.path.join(self.datadir, "owl_rgba_img.png")
        # ENVI hyperspectral data
        self.envi_bil_file = os.path.join(self.datadir, "darkReference")
        # Thermal image
        self.thermal_img = os.path.join(self.datadir, "FLIR2600.csv")
        # Thermal image data
        self.thermal_obj_file = os.path.join(self.datadir, "thermal_img.npz")
        # Thermal image mask
        self.thermal_mask = os.path.join(self.datadir, "thermal_img_mask.png")
        # Bayer image
        self.bayer_img = os.path.join(self.datadir, "bayer_img.png")

    def load_hsi(self, pkl_file):
        """Load PlantCV Spectral_data pickled object."""
        with open(pkl_file, "rb") as fp:
            return pkl.load(fp)

    def load_contours(self, npz_file):
        """Load data saved in a NumPy .npz file."""
        data = np.load(npz_file, encoding="latin1")
        return data['contours'], data['hierarchy']

    def load_composed_contours(self, npz_file):
        """Load data saved in a NumPy .npz file."""
        data = np.load(npz_file, encoding="latin1")
        return data['contour']

    def load_npz(self, npz_file):
        """Load data saved in a NumPy .npz file."""
        data = np.load(npz_file, encoding="latin1")
        return data['arr_0']


@pytest.fixture(scope="session")
def test_data():
    return TestData()
