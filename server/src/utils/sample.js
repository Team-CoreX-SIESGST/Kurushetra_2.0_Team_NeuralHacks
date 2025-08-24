export const text = `Deep Learning for ECG Analysis: Benchmarks and Insights from PTB-XL
(IEEE Journal of Biomedical and Health Informatics, Vol. 25, No. 5, May 2021)

Authors: Nils Strodthoff, Patrick Wagner, Tobias Schaeffter, Wojciech Samek

Abstract:
The paper introduces benchmark results for ECG analysis using the PTB-XL dataset, a large 12-lead ECG dataset. It evaluates deep learning models (ResNet, Inception, CNNs, RNNs) across prediction tasks like ECG statement classification, age, and sex prediction. ResNet and Inception-based models outperform others. Transfer learning from PTB-XL to ICBEB2018 dataset shows promising results, especially for small datasets. The study also addresses hidden stratification, model uncertainty, and interpretability, highlighting their importance in clinical applications.

Key Contributions:

Benchmarking tasks on PTB-XL: ECG statement prediction, age, sex prediction.

Implementation of CNN, ResNet, Inception, and RNN models.

Demonstrated transfer learning from PTB-XL to ICBEB2018 dataset.

Analysis of hidden stratification, diagnosis likelihood vs. model uncertainty, interpretability.

Datasets Used:

PTB-XL: 21,837 12-lead ECGs (10s each) from 18,885 patients (52% male, 48% female).

ICBEB2018: 6,877 ECGs (6–60s each), annotated with 9 diagnostic classes.

Main Findings:

CNNs (ResNet, InceptionTime) achieve the highest AUC scores (0.89–0.96 across tasks).

RNNs perform slightly worse but remain competitive.

Feature-based (wavelet + NN) methods underperform compared to deep learning.

Transfer learning with PTB-XL improves results on ICBEB2018, especially for small training sets.

Age regression achieved ~7-year MAE, sex prediction ~85–90% accuracy.

Hidden stratification: some ECG subclasses (e.g., IVCD, NST_) show weak performance masked by superclass accuracy.

Model uncertainty correlates with diagnosis likelihoods assigned by cardiologists.

Interpretability: relevance maps highlight physiologically meaningful ECG features (PVC, pacemaker signals).

Conclusion:
PTB-XL serves as a valuable benchmarking dataset for ECG analysis. Modern CNN architectures like xresnet1d101 and InceptionTime outperform others. Transfer learning is effective in small datasets. Future directions include interpretability, robustness, and handling hidden stratification.

Resources:

Dataset: PTB-XL on PhysioNet

Code: GitHub Repository`;
