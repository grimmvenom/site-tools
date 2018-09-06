#-----------------------------------------------------------------------------
# Copyright (c) 2017, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License with exception
# for distributing bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------


"""
Fixes issue #2978 with pandas version 0.21
(Pandas missing `pandas._libs.tslibs.timedeltas.so`)

MacOSX:
/usr/local/lib/python3.6/site-packages/PyInstaller/hooks/hook-pandas.py

Windows:
%AppData%\Local\Programs\Python\Python36\Lib\site-packages\Pyinstaller\hooks\hook-pandas.py

Linux:
/usr/lib/python3.6/site-packages/PyInstaller/hooks/hook-pandas.py
/usr/local/lib/python3.6/site-packages/PyInstaller/hooks/hook-pandas.py
"""


hiddenimports = ['pandas._libs.tslibs.np_datetime','pandas._libs.tslibs.nattype','pandas._libs.skiplist']
