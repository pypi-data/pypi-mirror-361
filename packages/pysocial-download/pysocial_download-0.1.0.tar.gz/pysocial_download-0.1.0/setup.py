from setuptools import setup, find_packages

setup(
    name='pysocial-download',
    version='0.1.0',
    description='Bibliothèque simple pour télécharger des vidéos YouTube, Facebook, TikTok, etc. avec yt-dlp',
    author='TonNom',
    author_email='ton@email.com',
    packages=find_packages(),
    install_requires=[
        'yt-dlp>=2023.0.0',
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            # Optionnel : ligne de commande 'pysocial' liée au CLI (si tu crées un cli.py)
            # 'pysocial=pysocial.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
