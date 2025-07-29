import os
import numpy as np
from abc import ABC, abstractmethod
from .ReconEnums import ReconType
from AOT_biomaps.Config import config
from AOT_biomaps.AOT_Experiment.Tomography import Tomography
from sklearn.metrics import mean_squared_error
from skimage.metrics import structural_similarity as ssim

class Recon(ABC):
    def __init__(self, experiment, saveDir, isGPU = config.get_process() == 'gpu',  isMultiGPU =  True if config.numGPUs > 1 else False, isMultiCPU = True):
        self.reconPhantom = None
        self.reconLaser = None
        self.experiment = experiment
        self.reconType = None
        self.saveDir = saveDir
        self.MSE = None
        self.SSIM = None

        self.isGPU = isGPU
        self.isMultiGPU = isMultiGPU
        self.isMultiCPU = isMultiCPU

        if str(type(self.experiment)) != str(Tomography):
            raise TypeError(f"Experiment must be of type {Tomography}")

    @abstractmethod
    def run(self,withTumor = True):
        pass

    def calculateCRC(self,iteration,ROI_mask = None):
        """
        Computes the Contrast Recovery Coefficient (CRC) for a given ROI.
        """
        if self.reconType is ReconType.Analytic:
            raise TypeError(f"Impossible to calculate CRC with analytical reconstruction")
        elif self.reconType is None:
            raise ValueError("Run reconstruction first")
        
        if self.reconLaser is None or self.reconLaser == []:
            raise ValueError("Reconstructed laser is empty. Run reconstruction first.")
        if isinstance(self.Laser,list) and len(self.Laser) == 1:
            raise ValueError("Reconstructed Image without tumor is a single frame. Run reconstruction with isSavingEachIteration=True to get a sequence of frames.")
        if self.reconPhantom is None or self.reconPhantom == []:
            raise ValueError("Reconstructed phantom is empty. Run reconstruction first.")
        if isinstance(self.reconPhantom, list) and len(self.reconPhantom) == 1:
            raise ValueError("Reconstructed Image with tumor is a single frame. Run reconstruction with isSavingEachIteration=True to get a sequence of frames.")
        
        if self.reconLaser is None or self.reconLaser == []:
            print("Reconstructed laser is empty. Running reconstruction without tumor...")
            self.run(withTumor = False, isSavingEachIteration=True)
        if ROI_mask is not None:
            recon_ratio = np.mean(self.reconPhantom[iteration][ROI_mask]) / np.mean(self.reconLaser[iteration][ROI_mask])
            lambda_ratio = np.mean(self.experiment.OpticImage.phantom[ROI_mask]) / np.mean(self.experiment.OpticImage.laser[ROI_mask]) 
        else:
            recon_ratio = np.mean(self.reconPhantom[iteration]) / np.mean(self.reconLaser[iteration])
            lambda_ratio = np.mean(self.experiment.OpticImage.phantom) / np.mean(self.experiment.OpticImage.laser)
        
        # Compute CRC
        CRC = (recon_ratio - 1) / (lambda_ratio - 1)
        return CRC
    
    def calculateMSE(self):
        """
        Calculate the Mean Squared Error (MSE) of the reconstruction.

        Returns:
            mse: float or list of floats, Mean Squared Error of the reconstruction
        """
                
        if self.reconPhantom is None or self.reconPhantom == []:
            raise ValueError("Reconstructed phantom is empty. Run reconstruction first.")

        if self.reconType in (ReconType.Analytic, ReconType.DeepLearning):
            self.MSE = mean_squared_error(self.experiment.OpticImage.phantom, self.reconPhantom)

        elif self.reconType in (ReconType.Algebraic, ReconType.Bayesian):
            self.MSE = []
            for theta in self.reconPhantom:
                self.MSE.append(mean_squared_error(self.experiment.OpticImage.phantom, theta))
  
    def calculateSSIM(self):
        """
        Calculate the Structural Similarity Index (SSIM) of the reconstruction.

        Returns:
            ssim: float or list of floats, Structural Similarity Index of the reconstruction
        """

        if self.reconPhantom is None or self.reconPhantom == []:
            raise ValueError("Reconstructed phantom is empty. Run reconstruction first.")
    
        if self.reconType in (ReconType.Analytic, ReconType.DeepLearning):
            data_range = self.reconPhantom.max() - self.reconPhantom.min()
            self.SSIM = ssim(self.experiment.OpticImage.phantom, self.reconPhantom, data_range=data_range)

        elif self.reconType in (ReconType.Algebraic, ReconType.Bayesian):
            self.SSIM = []
            for theta in self.reconPhantom:
                data_range = theta.max() - theta.min()
                ssim_value = ssim(self.experiment.OpticImage.phantom, theta, data_range=data_range)
                self.SSIM.append(ssim_value)
 
    @staticmethod
    def load_recon(hdr_path):
        """
        Lit un fichier Interfile (.hdr) et son fichier binaire (.img) pour reconstruire une image comme le fait Vinci.
        
        Paramètres :
        ------------
        - hdr_path : chemin complet du fichier .hdr
        
        Retour :
        --------
        - image : tableau NumPy contenant l'image
        - header : dictionnaire contenant les métadonnées du fichier .hdr
        """
        header = {}
        with open(hdr_path, 'r') as f:
            for line in f:
                if ':=' in line:
                    key, value = line.split(':=', 1)  # s'assurer qu'on ne coupe que la première occurrence de ':='
                    key = key.strip().lower().replace('!', '')  # Nettoyage des caractères
                    value = value.strip()
                    header[key] = value
        
        # 📘 Obtenez le nom du fichier de données associé (le .img)
        data_file = header.get('name of data file')
        if data_file is None:
            raise ValueError(f"Impossible de trouver le fichier de données associé au fichier header {hdr_path}")
        
        img_path = os.path.join(os.path.dirname(hdr_path), data_file)
        
        # 📘 Récupérer la taille de l'image à partir des métadonnées
        shape = [int(header[f'matrix size [{i}]']) for i in range(1, 4) if f'matrix size [{i}]' in header]
        if shape and shape[-1] == 1:  # Si la 3e dimension est 1, on la supprime
            shape = shape[:-1]  # On garde (192, 240) par exemple
        
        if not shape:
            raise ValueError("Impossible de déterminer la forme de l'image à partir des métadonnées.")
        
        # 📘 Déterminez le type de données à utiliser
        data_type = header.get('number format', 'short float').lower()
        dtype_map = {
            'short float': np.float32,
            'float': np.float32,
            'int16': np.int16,
            'int32': np.int32,
            'uint16': np.uint16,
            'uint8': np.uint8
        }
        dtype = dtype_map.get(data_type)
        if dtype is None:
            raise ValueError(f"Type de données non pris en charge : {data_type}")
        
        # 📘 Ordre des octets (endianness)
        byte_order = header.get('imagedata byte order', 'LITTLEENDIAN').lower()
        endianess = '<' if 'little' in byte_order else '>'
        
        # 📘 Vérifie la taille réelle du fichier .img
        img_size = os.path.getsize(img_path)
        expected_size = np.prod(shape) * np.dtype(dtype).itemsize
        
        if img_size != expected_size:
            raise ValueError(f"La taille du fichier img ({img_size} octets) ne correspond pas à la taille attendue ({expected_size} octets).")
        
        # 📘 Lire les données binaires et les reformater
        with open(img_path, 'rb') as f:
            data = np.fromfile(f, dtype=endianess + np.dtype(dtype).char)
        
        image =  data.reshape(shape[::-1]) 
        
        # 📘 Rescale l'image si nécessaire
        rescale_slope = float(header.get('data rescale slope', 1))
        rescale_offset = float(header.get('data rescale offset', 0))
        image = image * rescale_slope + rescale_offset
        
        return image.T
