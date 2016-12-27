Name: scidavis
Version: 1.14
Release: alt2

Summary: SciDAVis is a free interactive application aimed at data analysis and publication-quality plotting. It combines a shallow learning curve and an intuitive, easy-to-use graphical user interface with powerful features such as scriptability and extensibility. SciDAVis runs on GNU/Linux, Windows and MacOS X; possibly also on other platforms like *BSD, although this is untested.
License: GPL2+
Group: Engineering
Url: http://scidavis.sourceforge.net/

Packager: Sample Maintainer <samplemaintainer@altlinux.org>
Source: %name-%version.tar
Patch0: scidavis-qt-translation-load.patch


BuildPreReq: gcc5-c++, zlib-devel, libmuparser-devel libqt4-devel libqt4-webkit-devel libqt4-assistant-devel qt4-mobility-devel qt4-qmf-devel qt4-devel libqtspell-qt4-devel python python-module-PyQt4 python-module-PyQt4-devel python-module-sip python-module-sip-devel

%description
SciDAVis is a free interactive application aimed at data
analysis and publication-quality plotting. It combines a
shallow learning curve and an intuitive, easy-to-use graphical
user interface with powerful features such as scriptability and
extensibility. SciDAVis runs on GNU/Linux, Windows and MacOS X;
possibly also on other platforms like *BSD, although this
is untested.

SciDAVis is similar in its field of application to proprietary Windows
applications like Origin and SigmaPlot as well as free applications
like QtiPlot, Labplot and Gnuplot.

What sets SciDAVis apart from the above is its emphasis on providing
a friendly and open environment (in the software as well as the
project) for new and experienced users alike. Particularly, this
means that we will try to provide good documentation on all levels,
ranging from users manual over tutorials down to and including
documentation of the internal APIs We encourage users to share
their experiences on our forums and on our mailing lists.






%prep
%setup
%patch0 -p0




%build
# we have unmodified upstream directory, added dl/ into it with gsl, qwt, qwtplot3d tarballs

# %%name failed to compile with system's libgsl (1.16), so we compile gsl inside sources and link with it statically. Here we unpack gsl
pushd 3rdparty
tar -x -f ../dl/gsl-1.16.tar.gz
mv gsl-1.16 gsl
popd

# unpack qwt
pushd 3rdparty
tar -x -f ../dl/qwt-5.2.3.tar.bz2
mv qwt-5.2.3 qwt
popd

# unpack qwtplot3d
pushd 3rdparty
tar -x -f ../dl/qwtplot3d-0.2.7.tgz
popd


# static lib in qwt or qwtplot3d will be included into plugins, which are shared objects (.so). So, fPIC is necessary (or ld will tell about it)
find -name "*.pro" -exec bash -c "echo -en \"\\nQMAKE_CXX_FLAGS += -fPIC\\n\" >> {}" \;



# compile gsl static libs and install to ~/fs
pushd 3rdparty/gsl
%autoreconf
mkdir -p ~/fs
./configure --disable-shared --enable-static --prefix=${HOME}/fs --with-pic
%make_build
make install
popd

# add ~/fs/inlcude and ../3rdparty/qwt/src to -I C++ flags for main project and it's lib
echo -en "\n\nINCLUDEPATH += /usr/src/fs/include ../3rdparty/qwt/src\n" >> libscidavis/libscidavis.pro
echo -en "\n\nINCLUDEPATH += /usr/src/fs/include ../3rdparty/qwt/src\n" >> scidavis/scidavis.pro

# compile qwt static library
pushd 3rdparty/qwt
# 1st comment out line requesting shared object. We want only static lib
sed -i.bak s/CONFIG\\s*\+=\\s*QwtDll/#\\0/g qwtconfig.pri
rm qwtconfig.pri.bak -fv
qmake-qt4
%make_build
popd

# compile qwtplot3d static lib
pushd 3rdparty/qwtplot3d
# add 2 includes to .h file
  cp include/qwt3d_openglhelper.h include/qwt3d_openglhelper.h.orig
  echo -en "#include <GL/gl.h>\n#include <GL/glu.h>\n" > include/qwt3d_openglhelper.h
  cat include/qwt3d_openglhelper.h.orig >> include/qwt3d_openglhelper.h
# request static lib, as upstream suggested
echo -en "\nCONFIG += staticlib\n" >> qwtplot3d.pro
qmake-qt4
%make_build
popd

# line "python{include(python.pri)}" becomes "include(python.pri)"
sed -i.bak "s/python\\s*{\\s*include\\s*\\(\\s*python.pri\\s*\\)\\s*}/include\\( python.pri \\)/g" scidavis/scidavis.pro
rm scidavis/scidavis.pro.bak -fv
# add LIBS
echo -en "\nLIBS += -L/usr/src/fs/lib -L../3rdparty/qwt/lib -L../3rdparty/qwtplot3d/lib\n" >> scidavis/scidavis.pro
pushd libscidavis
# link include directory, since files here have #include "qwtplot3d/xxx.h" or similar
ln -s ../3rdparty/qwtplot3d/include qwtplot3d
popd
# add include path to gsl into all .pro files
find -name "*.pro" -exec bash -c "echo -en \"\\nINCLUDEPATH += /usr/src/fs/include\\n\" >> {}" \;
# add lib path to gsl, and add lib paths to qwt, qwtplot3d
find -name "*.pro" -exec bash -c "echo -en \"\\nLIBS += -L/usr/src/fs/lib -L/usr/src/RPM/BUILD/%name-%version/3rdparty/qwt/lib -L/usr/src/RPM/BUILD/%name-%version/3rdparty/qwtplot3d/lib\\n\" >> {}" \;


# set qmPath to /usr/share/%%name/translations
sed -i.bak s/^\\s*qmPath\\s*=\\s*TS_PATH\\s*\;\\s*\$/qmPath=\"\\/usr\\/share\\/%name\\/translations\"\;/g libscidavis/src/ApplicationWindow.cpp
rm libscidavis/src/ApplicationWindow.cpp.bak -fv

qmake-qt4
%make_build



%install
mkdir -p %buildroot
make INSTALL_ROOT=%buildroot install

mkdir -p %buildroot/usr/share/applications
#cat <<EOF > %%buildroot/usr/share/applications/scidavis.desktop
#[Desktop Entry]
#Name=SciDAVis
#Exec=/usr/bin/scidavis
#Icon=scidavis
#Terminal=false
#Type=application
#Categories=Engineering
#
#EOF
cp scidavis/scidavis.desktop %buildroot/usr/share/applications/

cp scidavis-logo.svg %buildroot/usr/share/doc/scidavis
mkdir -p %buildroot/usr/share/pixmaps
cp scidavis/icons/scidavis.ico %buildroot/usr/share/pixmaps/


mkdir -p %buildroot/usr/share/icons/%name
pushd scidavis/icons
for i in * ; do
  cp -r $i %buildroot/usr/share/icons/%name/
done
popd

mkdir -p %buildroot/usr/share/%name/translations
find -name "*.qm" -exec cp "{}" %buildroot/usr/share/%name/translations/ \;
#find -name "*.ts" -exec cp "{}" %buildroot/usr/share/%name/translations/ \;


#fix .desktop file
sed -i.bak s/^Icon=scidavis\$/Icon=\\/usr\\/share\\/icons\\/%name\\/scidavis.ico/g %buildroot/usr/share/applications/%name.desktop
rm %buildroot/usr/share/applications/%name.desktop.bak -fv

##fix .desktop file
#sed -i.bak s/^Categories=.*\$/Categories=DataVisualization/g %buildroot/usr/share/applications/%name.desktop
#rm %buildroot/usr/share/applications/%name.desktop.bak -fv

mkdir -p %buildroot/usr/share/mime/packages
cp scidavis/scidavis.xml %buildroot/usr/share/mime/packages/

%find_lang %name


%files -f %name.lang
%doc CHANGES INSTALL.md README.installer README.md
/usr/share/icons/%name
/usr/bin/*
/usr/share/doc/scidavis
/usr/share/applications/*
/usr/lib/scidavis
/usr/share/pixmaps/*
/usr/share/%name/translations
/usr/share/mime/packages/*

%changelog
* Sun Nov 30 2016 Sample Maintainer <samplemaintainer@altlinux.org> 1.14-alt2
- initial build

