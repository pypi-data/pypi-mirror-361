# OpenDVP

[![Docs](https://img.shields.io/badge/docs-online-blue.svg)](https://coscialab.github.io/openDVP/)
[![CI](https://github.com/CosciaLab/openDVP/actions/workflows/testing.yml/badge.svg)](https://github.com/CosciaLab/openDVP/actions/workflows/testing.yml)
[![Python versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Platforms](https://img.shields.io/badge/platform-linux%20%7C%20windows%20%7C%20macos-lightgrey.svg)](https://github.com/CosciaLab/openDVP/actions/workflows/testing.yml)
[![PyPI version](https://img.shields.io/pypi/v/openDVP.svg)](https://pypi.org/project/openDVP/)
[![License](https://img.shields.io/github/license/CosciaLab/openDVP.svg)](https://github.com/CosciaLab/opendvp/blob/main/LICENSE)
[![codecov](https://codecov.io/gh/CosciaLab/openDVP/graph/badge.svg?token=IWGKMCHAA1)](https://codecov.io/gh/CosciaLab/openDVP)

<img width="853" height="602" alt="Screenshot 2025-07-10 at 13 11 28" src="https://github.com/user-attachments/assets/15c4445e-b0c7-4734-945c-3d664ded4b00" />


**OpenDVP** is an open-source framework designed to support Deep Visual Proteomics (DVP) across multiple modalities using community-supported tools.

---

## Overview

OpenDVP empowers researchers to perform Deep Visual Proteomics using open-source software. It integrates with community data standards such as [AnnData](https://anndata.readthedocs.io/en/latest/) and [SpatialData](https://spatialdata.scverse.org/) to ensure interoperability with popular analysis tools like [Scanpy](https://github.com/scverse/scanpy), [Squidpy](https://github.com/scverse/squidpy), and [Scimap](https://github.com/labsyspharm/scimap).

This repository outlines four major use cases for OpenDVP:

1. **Image Processing and Analysis**
2. **Matrix Processing and Analysis**
3. **Quality Control with QuPath and Napari**
4. **Exporting to LMD (Laser Microdissection)**

## Installation

You can install openDVP via pip:
```bash
pip install opendvp
```

## Motivation

Deep Visual Proteomics (DVP) combines high-dimensional imaging, spatial analysis, and machine learning to extract complex biological insights from tissue samples. However, many current DVP tools are locked into proprietary formats, restricted software ecosystems, or closed-source pipelines that limit reproducibility, accessibility, and community collaboration.

- Work transparently across modalities and analysis environments
- Contribute improvements back to a growing ecosystem
- Avoid vendor lock-in for critical workflows

## Qupath-to-LMD

[Qupath-to-LMD Webapp](https://qupath-to-lmd-mdcberlin.streamlit.app/)

[![Tutorial](https://img.youtube.com/vi/jimBIqGUaXg/0.jpg)](https://www.youtube.com/watch?v=jimBIqGUaXg&t=2s)

## Community & Discussions

We are excited to hear from you and together we can improve spatial protemics.
We welcome questions, feedback, and community contributions!  
Join the conversation in the [GitHub Discussions](https://github.com/CosciaLab/opendvp/discussions) tab.


## Citation

Please cite the corresponding bioarxiv for now, Coming Soon!

## Demo data
A comprehensive tutorial of openDVP features is on the works, to test it, feel free to download our demo data.

https://zenodo.org/records/15397560
