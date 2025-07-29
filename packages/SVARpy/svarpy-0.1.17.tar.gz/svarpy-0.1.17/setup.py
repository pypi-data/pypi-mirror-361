import setuptools
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")
license_text = (this_directory / "LICENSE").read_text(encoding="utf-8")

# Read requirements.txt, handling FileNotFoundError
try:
  requirements = (this_directory / "requirements.txt").read_text(encoding="utf-8").splitlines()
except FileNotFoundError:
  requirements = []
  print("Warning: requirements.txt not found. Proceeding without dependencies.")

setuptools.setup(
  name="SVARpy",
  version="0.1.17",
  author="Sascha Keweloh",
  author_email="sascha.keweloh@tu-dortmund.de",
  description="SVAR estimation",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/Saschakew/SVARpy",
  packages=setuptools.find_packages(),
  install_requires=requirements,
  python_requires='>=3.7',
  license=license_text,
  classifiers=[
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
  ],
)
