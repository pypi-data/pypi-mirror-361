from setuptools import setup, find_packages
import pathlib
import os

here = pathlib.Path(__file__).parent.resolve()
version = {}
version_file = os.path.join(os.path.dirname(__file__), "scBridge", "version.py")
with open(version_file) as f:
    exec(f.read(), version)
    
setup(
    name="scBridge",
    version=version["__version__"],
    description="A single-cell cross-modality translation method specifically between RNA data and DNA methylation data.",
    long_description="We present scBridge, a sophisticated framework for bidirectional cross-modal translation between scRNA-seq and scDNAm profiles with broad biological applicability. scBridge adopts a dual-channel variational autoencoder (VAE) architecture to project scRNA-seq and scDNAm data into a unified latent space, enabling effective cross-modal alignment and translation. To adaptively capture the context-dependent DNA methylation patterns related to gene regulation, we introduce Mixture-of-Experts (MoE) mechanism, which introduces a gating network to dynamically assign input cells to specialized expert subnetworks. .",
    license="MIT Licence",
    author="PiperL",
    classifiers=[
        "Programming Language :: Python :: 3.9",
    ],
    keywords="single cell, cross-modality translation, DNA Methylation",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        'scanpy>=1.9.1',
        'torch>=1.12.1',
        'torchvision>=0.13.1',
        'torchaudio>=0.12.1',
        'scikit-learn>=1.1.3',
        'scvi-tools==0.19.0',
        'scvi-colab',
        'scipy==1.9.3',
        'episcanpy==0.3.2',
        'seaborn>=0.11.2',
        'matplotlib>=3.6.2',
        'pot==0.9.0',
        'torchmetrics>=0.11.4',
        'leidenalg',
        'pybedtools',
        'adjusttext',
        'jupyter'
    ]
)