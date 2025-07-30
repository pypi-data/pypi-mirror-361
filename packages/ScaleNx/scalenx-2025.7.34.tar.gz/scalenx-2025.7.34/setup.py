import setuptools

with open('README.md') as file:
    read_me_md = file.read()

setuptools.setup(
    name='ScaleNx',
    version='2025.7.34',
    author='Ilya Razmanov',
    author_email='ilyarazmanov@gmail.com',
    description='Image resizing using Scale2x, Scale3x, Scale2xSFX and Scale3xSFX algorithms, in pure Python.',
    long_description=read_me_md,
    long_description_content_type='text/markdown',
    url='https://dnyarri.github.io/',
    project_urls={
        'Source': 'https://github.com/Dnyarri/PixelArtScaling',
        'Changelog': 'https://github.com/Dnyarri/PixelArtScaling/blob/py34/CHANGELOG.md',
        'Issues': 'https://github.com/Dnyarri/PixelArtScaling/issues',
    },
    packages=['scalenx'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'License :: OSI Approved :: The Unlicense (Unlicense)',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Scientific/Engineering :: Image Processing',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
    ],
    keywords=['Scale2x', 'Scale3x', 'Scale2xSFX', 'Scale3xSFX,AdvMAME2', 'AdvMAME3', 'pixel', 'resize', 'rescale', 'image', 'bitmap', 'python'],
    python_requires='>=3.4',
)
