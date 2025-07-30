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
    name="llm_dataset_converter_all",
    description="Meta-library that combines all llm-dataset-converter libraries.",
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
        "llm_dataset_converter>=0.2.7",
        "ldc_doc>=0.0.5",
        "ldc_docx>=0.0.4",
        "ldc_faster-whisper>=0.0.3",
        "ldc_gitingest>=0.0.2",
        "ldc_google>=0.0.2",
        "ldc_html>=0.0.3",
        "ldc_openai>=0.0.2",
        "ldc_pdf>=0.0.4",
        "ldc_tint>=0.0.3",
    ],
    version="0.0.6",
    author='Peter Reutemann',
    author_email='fracpete@waikato.ac.nz',
)
