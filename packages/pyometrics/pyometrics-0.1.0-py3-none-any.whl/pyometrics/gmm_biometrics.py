import os
import pickle
import numpy as np
import librosa
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

SUPPORTED_AUDIO_EXTENSIONS = (".wav", ".mp3", ".m4a", ".flac")

def extract_features(audio_path, n_mfcc=13):
    """
    Extract MFCC + delta features from a single audio file.
    Returns a (samples x features) array after scaling.
    """
    audio, sr = librosa.load(audio_path, sr=None)
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc)
    mfcc_delta = librosa.feature.delta(mfcc)

    combined = np.vstack([mfcc, mfcc_delta])  
    combined = combined.T 

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(combined)
    return scaled_features

def gather_features_from_folder(folder_path, n_mfcc=13, min_files=10):
    """
    Gathers features from all supported audio files in folder_path and concatenates them.
    
    :param folder_path: Path to folder containing audio files.
    :param n_mfcc:      Number of MFCC coefficients to extract.
    :param min_files:   Minimum number of audio files required. Defaults to 10.
    :return:            (total_frames, 2*n_mfcc) Numpy array.

    Raises ValueError if fewer than min_files audio are found.
    """
    all_features = []
    file_count = 0

    for fname in os.listdir(folder_path):
        if any(fname.lower().endswith(ext) for ext in SUPPORTED_AUDIO_EXTENSIONS):
            file_count += 1
            audio_path = os.path.join(folder_path, fname)
            feats = extract_features(audio_path, n_mfcc=n_mfcc)
            all_features.append(feats)

    if file_count < min_files:
        raise ValueError(
            f"Need at least {min_files} audio files to create a voice biometric. "
            f"Found {file_count} in '{folder_path}'."
        )

    combined_features = np.vstack(all_features)  
    return combined_features

def create_voice_biometric(folder_path, model_path, n_mfcc=13, min_files=10):
    """
    Trains a GMM on audio from folder_path and saves the model to model_path (.gmm).
    
    :param folder_path: Path to folder with >= min_files audio files.
    :param model_path:  Filename to save the GMM (e.g. 'my_biometric.gmm').
    :param n_mfcc:      Number of MFCC coefficients (default 13).
    :param min_files:   User can set how many files must exist. Defaults to 10.
    """
    features = gather_features_from_folder(folder_path, n_mfcc=n_mfcc, min_files=min_files)

    gmm = GaussianMixture(n_components=16, max_iter=200, covariance_type='diag', n_init=3)
    gmm.fit(features)

    with open(model_path, 'wb') as f:
        pickle.dump(gmm, f)

def compare_voice_biometric(audio_path, model_path, n_mfcc=13):
    """
    Loads a GMM from model_path and compares an audio file at audio_path,
    returning a log-likelihood score. The higher, the more similar.
    """
    with open(model_path, 'rb') as f:
        gmm_model = pickle.load(f)

    feats = extract_features(audio_path, n_mfcc=n_mfcc)
    score = gmm_model.score(feats)
    return score