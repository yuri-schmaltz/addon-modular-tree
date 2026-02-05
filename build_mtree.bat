python m_tree/install.py
python .github/scripts/copy_native_module.py --source-dir m_tree/binaries --dest-dir .
IF EXIST "%USERPROFILE%\\scoop\\apps\\mingw-winlibs\\current\\bin\\libgcc_s_seh-1.dll" COPY "%USERPROFILE%\\scoop\\apps\\mingw-winlibs\\current\\bin\\libgcc_s_seh-1.dll" ".\\libgcc_s_seh-1.dll"
IF EXIST "%USERPROFILE%\\scoop\\apps\\mingw-winlibs\\current\\bin\\libstdc++-6.dll" COPY "%USERPROFILE%\\scoop\\apps\\mingw-winlibs\\current\\bin\\libstdc++-6.dll" ".\\libstdc++-6.dll"
IF EXIST "%USERPROFILE%\\scoop\\apps\\mingw-winlibs\\current\\bin\\libwinpthread-1.dll" COPY "%USERPROFILE%\\scoop\\apps\\mingw-winlibs\\current\\bin\\libwinpthread-1.dll" ".\\libwinpthread-1.dll"


