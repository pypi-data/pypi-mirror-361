from setuptools import setup, find_packages

setup(
    name='pytorch2tflite',
    version='0.1.2',
    description='Convert PyTorch (.pt) models to TFLite format for mobile deployment.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Md.Hamid Hosen',
    author_email='mdhamidhosen4@gmail.com',
    url='https://github.com/hamidhosen42/pytorch2tflite',
    packages=find_packages(),
    install_requires=[
        'ultralytics',
        'torch',
        'onnx',
        'onnx-tf',
        'tensorflow'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License'
    ],
    python_requires='>=3.7',
    include_package_data=True,
)