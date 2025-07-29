# SVARpy

The SVARpy Python package aims to provide easy and quick access to the non-Gaussian moment-based estimators proposed in the following studies:

- Keweloh, Sascha Alexander. "A generalized method of moments estimator for structural vector autoregressions based on higher moments." Journal of Business & Economic Statistics 39.3 (2021): 772-782.

- Keweloh, Sascha Alexander, Stephan Hetzenecker, and Andre Seepe. "Monetary Policy and Information Shocks in a Block-Recursive SVAR." Journal of International Money and Finance (2023).

- Keweloh, Sascha Alexander. "A feasible approach to incorporate information in higher moments in structural vector autoregressions." (2021).

## Quick Install

To install SVARpy, use the following command:

> pip install SVARpy


## Overview

The [SVARpyExamples](https://github.com/Saschakew/SVARpyExamples) repository on GitHub contains notebooks providing a brief overview of the main functionalities of the package.

The notebooks can be accessed online:

1. **Intuition**: 
This notebook visualizes how leveraging dependency measures based on covariance, coskewness, and cokurtosis can be used to estimate a non-Gaussian SVAR.
[Notebook](https://colab.research.google.com/github/Saschakew/SVARpyExamples/blob/main/SVARpy-Intuition.ipynb)

2. **SVAR-GMM**: 
Overview on the implementation of the SVAR-GMM method in Keweloh (2021).
[Notebook](https://colab.research.google.com/github/Saschakew/SVARpyExamples/blob/main/SVARpy-SVARGMM.ipynb)

3. **Fast SVAR-GMM**: 
Overview on the implementation of the fast SVAR-GMM method in Keweloh (2021).
[Notebook](https://colab.research.google.com/github/Saschakew/SVARpyExamples/blob/main/SVARpy-SVARGMMfast.ipynb)

4. **SVAR-CUE**: 
Overview on the implementation of the continuous updating version of the SVAR-GMM method in Keweloh (2021).
[Notebook](https://colab.research.google.com/github/Saschakew/SVARpyExamples/blob/main/SVARpy-SVARCUE.ipynb)

5. **Block-Recursive SVAR**: 
Overview on how to pass block-recursive restrictions to the estimator, see Keweloh et al. (2023).
[Notebook](https://colab.research.google.com/github/Saschakew/SVARpyExamples/blob/main/SVARpy-SVARGMM-BlockRec.ipynb)

## References

Keweloh, Sascha Alexander. "A generalized method of moments estimator for structural vector autoregressions based on higher moments." Journal of Business & Economic Statistics 39.3 (2021): 772-782.

Keweloh, Sascha Alexander. "A feasible approach to incorporate information in higher moments in structural vector autoregressions." (2021b).

Keweloh, Sascha A., Stephan Hetzenecker, and Andre Seepe. "Monetary Policy and Information Shocks in a Block-Recursive SVAR." Journal of International Money and Finance (2023).

