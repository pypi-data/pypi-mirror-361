from setuptools import setup, find_packages

setup(
    name='mobile_recorder',
    version='0.1.0',
    description='Record Android device screens and run operations using uiautomator2',
    author='Ori Raisfeld',
    author_email='raisfeldori@gmail.com',
    url='https://github.com/raisfeld-ori/mobile_recorder',
    packages=find_packages(),
    install_requires=[
        'uiautomator2>=2.16.0',
    ],
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    include_package_data=True,
) 