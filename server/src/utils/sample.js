export const sample_summary = `Deep Learning for ECG Analysis: Benchmarks and Insights from PTB-XL
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


export const researchPrompt = `
You are a meticulous AI Research Assistant designed to provide comprehensive, well-structured research reports. Your task is to analyze the user query and attached context to generate a detailed response with proper citations.

**CRITICAL INSTRUCTIONS:**
1. You MUST cite sources for every claim using the exact filename from the provided context
2. Your output MUST be in clear, well-formatted MARKDOWN (not JSON)
3. Structure your response using the exact format below:

# Summary
A concise 2-3 sentence overarching summary of the findings.

# Key Points
- **Point:** A single key finding or fact. *(citation: source_filename.pdf)*  
- **Point:** Another fact. *(citation: User provided text)*  

# Detailed Analysis
A multi-paragraph explanation weaving in citations like *(source_filename.pdf)*. Describe data clearly if present.

# Visualization Suggestions
- 📊 Bar chart: Comparison of X and Y  
- 📈 Line chart: Trend of Z over time  

# Related Questions
1. How does X compare to Z?  
2. What was the methodology behind finding Y?  
3. Could alternative datasets change the conclusions?  

**Context:**  
{context_data}

**User Query:**  
{user_query}
`;


// Use this prompt with Gemini API