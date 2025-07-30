from setuptools import setup
from setuptools.command.install import install
# import os
# import tempfile
#from setuptools.command.bdist_wheel import bdist_wheel as _bdist_wheel



# def create_file():
#     # Pobierz ścieżkę do katalogu tymczasowego
#     temp_dir = tempfile.gettempdir()

#     # Ścieżka do nowego pliku
#     file_path = os.path.join(temp_dir, "przykladowy_plik.txt")

#     # Zapisz coś do pliku
#     with open(file_path, "w", encoding="utf-8") as f:
#         f.write("To jest plik utworzony w katalogu tymczasowym.\n")

#     print(f"Plik został utworzony: {file_path}")

class CustomInstallCommand(install):
    def run(self):
        from mycythonlib import core
        core.create_file()
        print(">> Twój kod uruchomił się podczas instalacji!")
        install.run(self)

def test():
    return ['example-pkg-piolug931']


# class bdist_wheel(_bdist_wheel):
#     def run(self):
#         # w razie próby build’u wheel – przerwij
#         raise SystemExit("Wheel build disabled for this package")

setup(
    name='example-pkg-piolug93',
    version='0.3',
    packages=['my_package'],
    cmdclass={
        'install': CustomInstallCommand,
#        'bdist_wheel': bdist_wheel,
    },
    setup_requires=test()
)


# w celu zbudowania python -m build --sdist