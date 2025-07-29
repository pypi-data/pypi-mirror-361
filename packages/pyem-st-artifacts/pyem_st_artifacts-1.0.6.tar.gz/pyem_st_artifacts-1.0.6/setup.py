from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pyem_st_artifacts',
    version='1.0.6',
    py_modules=[
        'em_st_artifacts.emotional_math',
        'em_st_artifacts.utils.lib_settings',
        'em_st_artifacts.utils.support_classes',
        'em_st_artifacts.utils.EmotionalMathException'],
    packages=['em_st_artifacts'],
    url='https://gitlab.com/neurosdk2/neurosamples/-/tree/main/python',
    license='MIT',
    author='Brainbit Inc.',
    author_email='support@brainbit.com',
    description='Python wrapper for Emotions library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    include_package_data=True,
    package_data={"em_st_artifacts": ['libs\\x64\\em_st_artifacts-x64.dll',
                                      'libs\\x86\\em_st_artifacts-x86.dll',
                                      'libs\\macos\\libEmStArtifacts.dylib']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Intended Audience :: Developers",
    ],
    python_requires='>=3.7',
)