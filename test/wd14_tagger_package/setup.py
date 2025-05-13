from setuptools import setup, find_packages

setup(
    name='wd14_tagger_api',
    version='0.1.0',
    description='A package for image tagging using WD14 models',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/wd14_tagger_api',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'Pillow',
        'huggingface_hub',
        'onnxruntime',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)