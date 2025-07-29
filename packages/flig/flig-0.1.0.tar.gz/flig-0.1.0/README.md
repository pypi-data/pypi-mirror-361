# FLEX: Frequency Layer Explanation

## Overview

This repository contains the implementation of **FLEX (Frequency Layer Explanation)**, a method designed to explain the predictions of deep neural networks (DNNs) for sleep stage classification using EEG data. FLEX combines **Integrated Gradients (IG)** with a frequency-domain transform (via the **Real Fast Fourier Transform (RFFT)**) to provide frequency-based attribution scores.

The method is particularly useful for understanding how different frequency components of EEG signals influence the predictions of a DNN, enhancing model interpretability in the context of sleep research.

*We will always talk about EEG Data in Sleep Research here, but in general this method can be used for a frequency-wise understanding of a model classifying time-series data.*

---

## Features

- **RFFT Transformation**: Input EEG signals are transformed into the frequency domain using the RFFT.
- **iRFFT Transformation**: The inverse RFFT (iRFFT) is implemented as the first layer in the DNN to process frequency-domain inputs.
- **Integrated Gradients Attribution**: Captum's IG method is used to compute relevance scores for frequency bands, providing insights into the features contributing to the model's predictions.

---

## Definition of FLEX
Let F be our model (DNN) and x be our input (EEG-Data). Then with $\bar{F} = F \circ iRFFT$ and $\bar{x} = RFFT(x)$ we get $$FLEX_i(F,x) = IG_i(\bar{F},\bar{x})$$, where $FLEX(F,x) = (FLEX_1(F,x), ..., FLEX_n(F,x))$ with $x \in R^n$.

---

## Installation

### Requirements
- Python 3.8+
- Required libraries:
 - `numpy`
 - `torch`
 - `captum`

### Install Dependencies
You can install the required Python libraries using `pip`:
```bash
pip install numpy torch captum
