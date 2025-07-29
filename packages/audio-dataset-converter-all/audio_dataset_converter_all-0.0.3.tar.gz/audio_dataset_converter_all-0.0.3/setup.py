from setuptools import setup


def _read(f):
    """
    Reads in the content of the file.
    :param f: the file to read
    :type f: str
    :return: the content
    :rtype: str
    """
    return open(f, 'rb').read()


setup(
    name="audio_dataset_converter_all",
    description="Meta-library that combines all audio-dataset-converter libraries.",
    long_description=(
            _read('DESCRIPTION.rst') + b'\n' +
            _read('CHANGES.rst')).decode('utf-8'),
    url="https://github.com/waikato-llm/audio-dataset-converter-all",
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Multimedia :: Sound/Audio :: Conversion',
    ],
    license='MIT License',
    install_requires=[
        "audio_dataset_converter>=0.0.3",
        "audio_dataset_converter_faster-whisper>=0.0.3",
        "audio_dataset_converter_redis>=0.0.2",
        "audio_dataset_converter_visualization>=0.0.3",
    ],
    version="0.0.3",
    author='Peter Reutemann',
    author_email='fracpete@waikato.ac.nz',
)
