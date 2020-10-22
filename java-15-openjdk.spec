# Use gcc instead of clang
%bcond_with gcc
%bcond_without system_jdk
# Without bootstrap, the package BuildRequires
# rpm-javamacros (which in turn requires this package)
# so jmod(*) and java(*) Provides: can be generated correctly.
%bcond_without bootstrap
# Using rpm's debug package splitter is suboptimal because OpenJDK
# packages various shared library files inside zip (jmod) packages.
# Those aren't seen by the splitter and therefore get insanely large.
# Better to use OpenJDK's own debuginfo splitter here even if it
# results in somewhat nonstandard locations for debuginfo files.
%global debug_package %{nil}

# OpenJDK builds a lot of underlinked libraries and tools...
%global _disable_ld_no_undefined 1
%global _jvmdir %{_prefix}/lib/jvm

%define major %(echo %{version} |cut -d. -f1)
%define ver %(echo %{version} |rev |cut -d. -f2- |rev)
%define minor ga
#For non-GA releases: %(echo %{version} |rev |cut -d. -f1 |rev)
# OpenJDK X requires OpenJDK >= X-1 to build -- so we need
# to determine the previous version to get build dependencies
# right
%define oldmajor %(echo $((%{major}-1)))

Name:		java-15-openjdk
Version:	15.0.0
Release:	1
Summary:	Java Runtime Environment (JRE) %{major}
Group:		Development/Languages
License:	GPLv2, ASL 1.1, ASL 2.0, LGPLv2.1
URL:		http://openjdk.java.net/
# Source must be packages from upstream's hg repositories using the
# update_package.sh script
# PROJECT_NAME=jdk-updates REPO_NAME=jdk14u VERSION=jdk-14+36 ./generate_source_tarball.sh
Source0:	jdk-updates-jdk%{major}u-jdk-%{major}-ga.tar.zst
# Extra tests
Source50:	TestCryptoLevel.java
Source51:	TestECDSA.java
# Used to create source tarballs - not used by the rpm build process itself
Source100:	remove-intree-libraries.sh
# Patches from Fedora
Patch0:		https://src.fedoraproject.org/rpms/java-openjdk/raw/master/f/rh1648249-add_commented_out_nss_cfg_provider_to_java_security.patch
Patch1:		https://src.fedoraproject.org/rpms/java-openjdk/raw/master/f/rh1648242-accessible_toolkit_crash_do_not_break_jvm.patch
Patch2:		https://src.fedoraproject.org/rpms/java-openjdk/raw/master/f/rh1648644-java_access_bridge_privileged_security.patch
Patch3:		https://src.fedoraproject.org/rpms/java-openjdk/raw/master/f/rh649512-remove_uses_of_far_in_jpeg_libjpeg_turbo_1_4_compat_for_jdk10_and_up.patch
Patch4:		https://src.fedoraproject.org/rpms/java-openjdk/raw/master/f/pr3183-rh1340845-support_fedora_rhel_system_crypto_policy.patch
# Patches from OpenMandriva
Patch1002:	java-12-compile.patch
Patch1003:	openjdk-15-nss-3.57.patch
Patch1004:	openjdk-12-system-harfbuzz.patch
#Patch1005:	openjdk-13-fix-build.patch
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	binutils
BuildRequires:	cups-devel
BuildRequires:	desktop-file-utils
BuildRequires:	fontconfig
BuildRequires:	xsltproc
BuildRequires:	zip
BuildRequires:	pkgconfig(freetype2)
BuildRequires:	giflib-devel
BuildRequires:	pkgconfig(alsa)
BuildRequires:	pkgconfig(gtk+-2.0)
BuildRequires:	pkgconfig(nss)
BuildRequires:	pkgconfig(lcms2)
BuildRequires:	pkgconfig(libjpeg)
BuildRequires:	pkgconfig(libpng)
BuildRequires:	pkgconfig(x11)
BuildRequires:	pkgconfig(xext)
BuildRequires:	pkgconfig(xi)
BuildRequires:	pkgconfig(xcomposite)
BuildRequires:	pkgconfig(xinerama)
BuildRequires:	pkgconfig(xrandr)
BuildRequires:	pkgconfig(xrender)
BuildRequires:	pkgconfig(xt)
BuildRequires:	pkgconfig(xtst)
BuildRequires:	pkgconfig(xproto)
# For testing
BuildRequires:	gdb
# For freebl
BuildRequires:	nss-static-devel
# Zero-assembler build requirement.
%ifnarch %{jit_arches}
BuildRequires:	pkgconfig(libffi)
%endif

# cacerts build requirement.
BuildRequires:	openssl

%if %{with system_jdk}
Provides:	jre-current = %{EVRD}
Provides:	java-current = %{EVRD}
%endif
%if %{with bootstrap}
# In a bootstrap build, we can't have jmod(*) dependencies
# because openjdk 12's jmod has no idea how to read openjdk
# 13's module files.
BuildRequires:	java-%{oldmajor}-openjdk-devel
# Let's provide some basics...
Provides:	jmod(java.base) = %{EVRD}
%else
BuildRequires:	rpm-javamacros
BuildRequires:	java-%{major}-openjdk-devel
%endif

# For compatibility with JPackage/Fedora/Mageia packaging
Provides:	java-%{major}-openjdk-headless = 1:%{version}-%{release}
Provides:	java-openjdk-headless = 1:%{version}-%{release}
Provides:	java-headless = 1:%{version}-%{release}

%description
OpenJDK Java runtime and development environment

# Macro for packaging individual jmod files
%define modpackage()\
%%package module-%{1}\
Summary: The Java %{1} module, provided by OpenJDK\
Group: Development/Languages\
%%description module-%{1}\
The Java %{1} module, provided by OpenJDK\
%%files module-%{1}\
%{_jvmdir}/java-%{major}-openjdk/jmods/%{1}.jmod

%package gui
Summary:	Graphical user interface libraries for OpenJDK %{major}
Group:		Development/Languages
%if %{with system_jdk}
Provides:	jre-gui-current = %{EVRD}
Provides:	java-gui-current = %{EVRD}
%endif
# We really need to require %{name} = %{EVRD}, but this gets
# messed up by the compatibility provides below
# (java-%{major}-openjdk == %{name})
# So we have to require one of the compatibility provides of
# the main package instead.
Requires:	java-%{major}-openjdk-headless = 1:%{version}-%{release}
# For compatibility with JPackage/Fedora/Mageia packaging
Provides:	java-%{major}-openjdk = %{EVRD}
Provides:	java-openjdk = %{EVRD}
Provides:	java = %{EVRD}

%description gui
Graphical user interface libraries for OpenJDK %{major}

%package devel
Summary:	Java Development Kit (JDK) %{major}
Group:		Development/Languages
%if %{with system_jdk}
Provides:	jdk-current = %{EVRD}
Provides:	java-current-devel = %{EVRD}
%endif
Requires:	rpm-javamacros
Requires:	%{name} = %{EVRD}
Suggests:	%{name}-gui = %{EVRD}
# For compatibility with JPackage/Fedora/Mageia packaging
Provides:	java-openjdk-devel = %{EVRD}
Provides:	java-devel = %{EVRD}

%description devel
Java Development Kit (JDK) %{major}

%package source
Summary:	Source files for the Java class library
Group:		Development/Languages
Recommends:	%{name} = %{EVRD}

%description source
Source files for the Java class library

%package demo
Summary:	Demo/Example applications for OpenJDK
Group:		Development/Languages

%description demo
Demo/Example applications for OpenJDK

%package debug
Summary:	Debug information for package %{name}
Group:		Development/Debug

%description debug
Debug information for package %{name}

%prep
%autosetup -p1 -n openjdk

EXTRA_CFLAGS="$(echo %{optflags} -fuse-ld=bfd -Wno-error -fno-delete-null-pointer-checks -Wformat -Wno-cpp -DSYSTEM_NSS -I%{_includedir}/nss -I%{_includedir}/nspr4 |sed -r -e 's|-O[0-9sz]*||;s|-Werror=format-security||g')"
EXTRA_CXXFLAGS="$EXTRA_CFLAGS"
%if %{with gcc}
EXTRA_CFLAGS="$EXTRA_CFLAGS -fno-lifetime-dse"
EXTRA_CXXFLAGS="$EXTRA_CFLAGS -fno-lifetime-dse"
%ifarch %{ix86}
# https://bugs.openjdk.java.net/browse/JDK-8199936
EXTRA_CFLAGS="$EXTRA_CFLAGS -mincoming-stack-boundary=2"
EXTRA_CXXFLAGS="$EXTRA_CXXFLAGS -mincoming-stack-boundary=2"
%endif
export CC=gcc
export CXX=g++
%else
%ifarch %{ix86}
# https://bugs.openjdk.java.net/browse/JDK-8199936
EXTRA_CFLAGS="$EXTRA_CFLAGS -mstack-alignment=16"
EXTRA_CXXFLAGS="$EXTRA_CXXFLAGS -mstack-alignment=16"
%endif
%endif

NUM_PROC="$(getconf _NPROCESSORS_ONLN)"
[ -z "$NUM_PROC" ] && NUM_PROC=8

mkdir build
cd build

%if %{with gcc}
export NM=gcc-nm
export AR=gcc-ar
%else
export NM=llvm-nm
export AR=llvm-ar
%endif

if ! bash ../configure \
	--prefix=%{_prefix} \
	--libdir=%{_libdir} \
	--sysconfdir=%{_sysconfdir} \
	--mandir=%{_mandir} \
%if %{with gcc}
	--with-toolchain-type=gcc \
%else
	--with-toolchain-type=clang \
%endif
	--with-boot-jdk=$(ls -d %{_jvmdir}/java-%{oldmajor}-openjdk-* |head -n1) \
	--with-vendor-name="OpenMandriva" \
	--with-vendor-url="http://openmandriva.org/" \
	--with-vendor-version-string="OpenMandriva-%{version}-%{release}" \
	--with-debug-level=release \
	--with-native-debug-symbols=external \
	--enable-unlimited-crypto \
	--with-freetype=system \
	--with-zlib=system \
	--with-giflib=system \
	--with-libjpeg=system \
	--with-libpng=system \
	--with-lcms=system \
	--with-stdc++lib=dynamic \
	--with-extra-cflags="$EXTRA_CFLAGS" \
	--with-extra-cxxflags="$EXTRA_CXXFLAGS" \
	--with-extra-ldflags="%{ldflags}" \
	--with-num-cores="$NUM_PROC" \
	--with-jobs="$NUM_PROC" \
%ifarch %{x86_64}
	--with-jvm-features=zgc \
%endif
	--disable-warnings-as-errors; then
		echo "Configure failed -- see config.log:"
		cat config.log
		exit 1
fi


%build
# YYYYYYYUUUUUCCCCCCCKKKKKK! The build process really needs more than
# 1024 files open at the same time!
ulimit -Sn 65536

# With LTO enabled, /tmp (tmpfs) tends to run out of space.
# Temporary LTO files for openjdk 12 easily take 50+ GB.
# Hopefully the build directory has more free space.
mkdir -p compilertemp
export TMPDIR="$(pwd)/compilertemp"

cd build
# We intentionally don't use %%make_build - OpenJDK doesn't like -j at all
make -j1 bootcycle-images all docs

%install
mkdir -p %{buildroot}%{_jvmdir}
cp -a build/images/jdk %{buildroot}%{_jvmdir}/java-%{major}-openjdk
ln -s java-%{major}-openjdk %{buildroot}%{_jvmdir}/jre-%{major}-openjdk

%if %{with system_jdk}
ln -s java-%{major}-openjdk %{buildroot}%{_jvmdir}/java-openjdk
ln -s java-%{major}-openjdk %{buildroot}%{_jvmdir}/java
ln -s java-%{major}-openjdk %{buildroot}%{_jvmdir}/jre-openjdk
ln -s java-%{major}-openjdk %{buildroot}%{_jvmdir}/jre

mkdir -p %{buildroot}%{_mandir}
mv %{buildroot}%{_jvmdir}/java-%{major}-openjdk/man/* %{buildroot}%{_mandir}
rmdir %{buildroot}%{_jvmdir}/java-%{major}-openjdk/man

mkdir -p %{buildroot}%{_sysconfdir}/ld.so.conf.d
echo %{_jvmdir}/java-%{major}-openjdk/lib >%{buildroot}%{_sysconfdir}/ld.so.conf.d/java.conf

mkdir -p %{buildroot}%{_sysconfdir}/profile.d
cat >%{buildroot}%{_sysconfdir}/profile.d/90java.sh <<'EOF'
export JAVA_HOME=%{_jvmdir}/java-%{major}-openjdk
export PATH=$PATH:$JAVA_HOME/bin
EOF
cat >%{buildroot}%{_sysconfdir}/profile.d/90java.csh <<'EOF'
setenv JAVA_HOME %{_jvmdir}/java-%{major}-openjdk
setenv PATH ${PATH}:${JAVA_HOME}/bin
EOF
chmod +x %{buildroot}%{_sysconfdir}/profile.d/*.*sh
%endif

%files
%if %{with system_jdk}
%dir %{_jvmdir}
%{_jvmdir}/java
%{_jvmdir}/java-openjdk
%{_jvmdir}/jre
%{_jvmdir}/jre-openjdk
%endif
%dir %{_jvmdir}/java-%{major}-openjdk/bin
%dir %{_jvmdir}/java-%{major}-openjdk/conf
%dir %{_jvmdir}/java-%{major}-openjdk/jmods
%{_jvmdir}/java-%{major}-openjdk/jmods/java.base.jmod
%dir %{_jvmdir}/java-%{major}-openjdk/legal
%dir %{_jvmdir}/java-%{major}-openjdk/lib
%config(noreplace) %{_jvmdir}/java-%{major}-openjdk/conf/*
%{_jvmdir}/java-%{major}-openjdk/release
%{_jvmdir}/java-%{major}-openjdk/bin/java
%{_jvmdir}/java-%{major}-openjdk/bin/jpackage
%{_jvmdir}/java-%{major}-openjdk/bin/keytool
%{_jvmdir}/java-%{major}-openjdk/bin/rmid
%{_jvmdir}/java-%{major}-openjdk/bin/rmiregistry
%{_jvmdir}/java-%{major}-openjdk/lib/classlist
%{_jvmdir}/java-%{major}-openjdk/lib/ct.sym
%{_jvmdir}/java-%{major}-openjdk/lib/jexec
%{_jvmdir}/java-%{major}-openjdk/lib/jfr
%{_jvmdir}/java-%{major}-openjdk/lib/jrt-fs.jar
%{_jvmdir}/java-%{major}-openjdk/lib/jspawnhelper
%{_jvmdir}/java-%{major}-openjdk/lib/jvm.cfg
%{_jvmdir}/java-%{major}-openjdk/lib/libattach.so
%{_jvmdir}/java-%{major}-openjdk/lib/libawt.so
%{_jvmdir}/java-%{major}-openjdk/lib/libawt_headless.so
%{_jvmdir}/java-%{major}-openjdk/lib/libdt_socket.so
%{_jvmdir}/java-%{major}-openjdk/lib/libextnet.so
%{_jvmdir}/java-%{major}-openjdk/lib/libfontmanager.so
%{_jvmdir}/java-%{major}-openjdk/lib/libinstrument.so
%{_jvmdir}/java-%{major}-openjdk/lib/libj2gss.so
%{_jvmdir}/java-%{major}-openjdk/lib/libj2pcsc.so
%{_jvmdir}/java-%{major}-openjdk/lib/libj2pkcs11.so
%{_jvmdir}/java-%{major}-openjdk/lib/libjaas.so
%{_jvmdir}/java-%{major}-openjdk/lib/libjavajpeg.so
%{_jvmdir}/java-%{major}-openjdk/lib/libjava.so
%{_jvmdir}/java-%{major}-openjdk/lib/libjdwp.so
%{_jvmdir}/java-%{major}-openjdk/lib/libjimage.so
%{_jvmdir}/java-%{major}-openjdk/lib/libjli.so
%{_jvmdir}/java-%{major}-openjdk/lib/libjsig.so
%{_jvmdir}/java-%{major}-openjdk/lib/libjsound.so
%{_jvmdir}/java-%{major}-openjdk/lib/liblcms.so
%{_jvmdir}/java-%{major}-openjdk/lib/libmanagement_agent.so
%{_jvmdir}/java-%{major}-openjdk/lib/libmanagement_ext.so
%{_jvmdir}/java-%{major}-openjdk/lib/libmanagement.so
%{_jvmdir}/java-%{major}-openjdk/lib/libmlib_image.so
%{_jvmdir}/java-%{major}-openjdk/lib/libnet.so
%{_jvmdir}/java-%{major}-openjdk/lib/libnio.so
%{_jvmdir}/java-%{major}-openjdk/lib/libprefs.so
%{_jvmdir}/java-%{major}-openjdk/lib/librmi.so
%{_jvmdir}/java-%{major}-openjdk/lib/libsaproc.so
%{_jvmdir}/java-%{major}-openjdk/lib/libsctp.so
%{_jvmdir}/java-%{major}-openjdk/lib/libsunec.so
%{_jvmdir}/java-%{major}-openjdk/lib/libverify.so
%{_jvmdir}/java-%{major}-openjdk/lib/libzip.so
%{_jvmdir}/java-%{major}-openjdk/lib/modules
%{_jvmdir}/java-%{major}-openjdk/lib/psfontj2d.properties
%{_jvmdir}/java-%{major}-openjdk/lib/psfont.properties.ja
%{_jvmdir}/java-%{major}-openjdk/lib/security
%{_jvmdir}/java-%{major}-openjdk/lib/server
%{_jvmdir}/java-%{major}-openjdk/lib/tzdb.dat
%doc %{_jvmdir}/java-%{major}-openjdk/legal/java.base
%doc %{_jvmdir}/java-%{major}-openjdk/legal/java.compiler
%doc %{_jvmdir}/java-%{major}-openjdk/legal/java.datatransfer
%doc %{_jvmdir}/java-%{major}-openjdk/legal/java.instrument
%doc %{_jvmdir}/java-%{major}-openjdk/legal/java.logging
%doc %{_jvmdir}/java-%{major}-openjdk/legal/java.management.rmi
%doc %{_jvmdir}/java-%{major}-openjdk/legal/java.management
%doc %{_jvmdir}/java-%{major}-openjdk/legal/java.naming
%doc %{_jvmdir}/java-%{major}-openjdk/legal/java.net.http
%doc %{_jvmdir}/java-%{major}-openjdk/legal/java.prefs
%doc %{_jvmdir}/java-%{major}-openjdk/legal/java.rmi
%doc %{_jvmdir}/java-%{major}-openjdk/legal/java.scripting
%doc %{_jvmdir}/java-%{major}-openjdk/legal/java.se
%doc %{_jvmdir}/java-%{major}-openjdk/legal/java.security.jgss
%doc %{_jvmdir}/java-%{major}-openjdk/legal/java.security.sasl
%doc %{_jvmdir}/java-%{major}-openjdk/legal/java.smartcardio
%doc %{_jvmdir}/java-%{major}-openjdk/legal/java.sql.rowset
%doc %{_jvmdir}/java-%{major}-openjdk/legal/java.sql
%doc %{_jvmdir}/java-%{major}-openjdk/legal/java.transaction.xa
%doc %{_jvmdir}/java-%{major}-openjdk/legal/java.xml.crypto
%doc %{_jvmdir}/java-%{major}-openjdk/legal/java.xml
%{_jvmdir}/jre-%{major}-openjdk
%if %{with system_jdk}
%{_mandir}/man1/java.1*
%{_mandir}/man1/jpackage.1*
%{_mandir}/man1/keytool.1*
%{_mandir}/man1/rmid.1*
%{_mandir}/man1/rmiregistry.1*
%{_mandir}/man1/jdeprscan.1*
%{_mandir}/man1/jfr.1*
%{_mandir}/man1/jhsdb.1*
%{_mandir}/man1/jlink.1*
%{_mandir}/man1/jmod.1*
%{_mandir}/man1/jshell.1*
%{_sysconfdir}/profile.d/*
%{_sysconfdir}/ld.so.conf.d/java.conf
%else
%dir %{_jvmdir}/java-%{major}-openjdk/man
%dir %{_jvmdir}/java-%{major}-openjdk/man/man1
%{_jvmdir}/java-%{major}-openjdk/man/man1/java.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/jpackage.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/keytool.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/rmid.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/rmiregistry.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/jdeprscan.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/jfr.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/jhsdb.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/jlink.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/jmod.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/jshell.1*
%endif

%files gui
%{_jvmdir}/java-%{major}-openjdk/lib/libawt_xawt.so
%{_jvmdir}/java-%{major}-openjdk/lib/libjawt.so
%{_jvmdir}/java-%{major}-openjdk/lib/libsplashscreen.so
%{_jvmdir}/java-%{major}-openjdk/jmods/java.desktop.jmod
%doc %{_jvmdir}/java-%{major}-openjdk/legal/java.desktop
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.unsupported.desktop

%files devel
%{_jvmdir}/java-%{major}-openjdk/include
%ifnarch %{ix86} %{arm}
%{_jvmdir}/java-%{major}-openjdk/bin/jaotc
%if %{with system_jdk}
%{_mandir}/man1/jaotc.1*
%else
%{_jvmdir}/java-%{major}-openjdk/man/man1/jaotc.1*
%endif
%endif
%{_jvmdir}/java-%{major}-openjdk/jmods/jdk.internal.ed.jmod
%{_jvmdir}/java-%{major}-openjdk/jmods/jdk.internal.jvmstat.jmod
%{_jvmdir}/java-%{major}-openjdk/jmods/jdk.internal.le.jmod
%{_jvmdir}/java-%{major}-openjdk/jmods/jdk.internal.opt.jmod
%{_jvmdir}/java-%{major}-openjdk/jmods/jdk.internal.vm.ci.jmod
%{_jvmdir}/java-%{major}-openjdk/jmods/jdk.internal.vm.compiler.jmod
%{_jvmdir}/java-%{major}-openjdk/jmods/jdk.internal.vm.compiler.management.jmod
%{_jvmdir}/java-%{major}-openjdk/jmods/jdk.internal.jvmstat.jmod
%{_jvmdir}/java-%{major}-openjdk/bin/jar
%{_jvmdir}/java-%{major}-openjdk/bin/jarsigner
%{_jvmdir}/java-%{major}-openjdk/bin/javac
%{_jvmdir}/java-%{major}-openjdk/bin/javadoc
%{_jvmdir}/java-%{major}-openjdk/bin/javap
%{_jvmdir}/java-%{major}-openjdk/bin/jcmd
%{_jvmdir}/java-%{major}-openjdk/bin/jconsole
%{_jvmdir}/java-%{major}-openjdk/bin/jdb
%{_jvmdir}/java-%{major}-openjdk/bin/jdeprscan
%{_jvmdir}/java-%{major}-openjdk/bin/jdeps
%{_jvmdir}/java-%{major}-openjdk/bin/jfr
%{_jvmdir}/java-%{major}-openjdk/bin/jhsdb
%{_jvmdir}/java-%{major}-openjdk/bin/jimage
%{_jvmdir}/java-%{major}-openjdk/bin/jinfo
%{_jvmdir}/java-%{major}-openjdk/bin/jlink
%{_jvmdir}/java-%{major}-openjdk/bin/jmap
%{_jvmdir}/java-%{major}-openjdk/bin/jmod
%{_jvmdir}/java-%{major}-openjdk/bin/jps
%{_jvmdir}/java-%{major}-openjdk/bin/jrunscript
%{_jvmdir}/java-%{major}-openjdk/bin/jshell
%{_jvmdir}/java-%{major}-openjdk/bin/jstack
%{_jvmdir}/java-%{major}-openjdk/bin/jstat
%{_jvmdir}/java-%{major}-openjdk/bin/jstatd
%{_jvmdir}/java-%{major}-openjdk/bin/serialver
%if %{with system_jdk}
%{_mandir}/man1/jar.1*
%{_mandir}/man1/jarsigner.1*
%{_mandir}/man1/javac.1*
%{_mandir}/man1/javadoc.1*
%{_mandir}/man1/javap.1*
%{_mandir}/man1/jcmd.1*
%{_mandir}/man1/jconsole.1*
%{_mandir}/man1/jdb.1*
%{_mandir}/man1/jdeps.1*
%{_mandir}/man1/jinfo.1*
%{_mandir}/man1/jmap.1*
%{_mandir}/man1/jps.1*
%{_mandir}/man1/jrunscript.1*
%{_mandir}/man1/jstack.1*
%{_mandir}/man1/jstat.1*
%{_mandir}/man1/jstatd.1*
%{_mandir}/man1/serialver.1*
%else
%{_jvmdir}/java-%{major}-openjdk/man/man1/jar.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/jarsigner.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/javac.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/javadoc.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/javap.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/jcmd.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/jconsole.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/jdb.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/jdeps.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/jinfo.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/jmap.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/jps.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/jrunscript.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/jstack.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/jstat.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/jstatd.1*
%{_jvmdir}/java-%{major}-openjdk/man/man1/serialver.1*
%endif
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.accessibility
%ifnarch %{ix86} %{arm}
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.aot
%endif
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.attach
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.charsets
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.compiler
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.crypto.cryptoki
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.crypto.ec
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.dynalink
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.editpad
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.hotspot.agent
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.httpserver
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.incubator.foreign
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.incubator.jpackage
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.internal.ed
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.internal.jvmstat
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.internal.le
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.internal.opt
%ifnarch %{ix86} %{arm}
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.internal.vm.ci
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.internal.vm.compiler.management
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.internal.vm.compiler
%endif
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.jartool
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.javadoc
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.jcmd
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.jconsole
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.jdeps
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.jdi
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.jdwp.agent
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.jfr
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.jlink
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.jshell
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.jsobject
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.jstatd
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.localedata
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.management.agent
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.management.jfr
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.management
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.naming.dns
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.naming.rmi
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.net
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.nio.mapmode
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.sctp
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.security.auth
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.security.jgss
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.unsupported
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.xml.dom
%doc %{_jvmdir}/java-%{major}-openjdk/legal/jdk.zipfs

%files demo
%{_jvmdir}/java-%{major}-openjdk/demo

%files source
%{_jvmdir}/java-%{major}-openjdk/lib/src.zip

%files debug
%{_jvmdir}/java-%{major}-openjdk/bin/*.debuginfo
%{_jvmdir}/java-%{major}-openjdk/lib/*.debuginfo

%modpackage java.compiler
%modpackage java.datatransfer
%modpackage java.instrument
%modpackage java.logging
%modpackage java.management
%modpackage java.management.rmi
%modpackage java.naming
%modpackage java.net.http
%modpackage java.prefs
%modpackage java.rmi
%modpackage java.scripting
%modpackage java.se
%modpackage java.security.jgss
%modpackage java.security.sasl
%modpackage java.smartcardio
%modpackage java.sql
%modpackage java.sql.rowset
%modpackage java.transaction.xa
%modpackage java.xml
%modpackage java.xml.crypto

%modpackage jdk.accessibility
%modpackage jdk.aot
%modpackage jdk.attach
%modpackage jdk.charsets
%modpackage jdk.compiler
%modpackage jdk.crypto.cryptoki
%modpackage jdk.crypto.ec
%modpackage jdk.dynalink
%modpackage jdk.editpad
%modpackage jdk.hotspot.agent
%modpackage jdk.httpserver
%modpackage jdk.incubator.foreign
%modpackage jdk.incubator.jpackage
%modpackage jdk.jartool
%modpackage jdk.javadoc
%modpackage jdk.jcmd
%modpackage jdk.jconsole
%modpackage jdk.jdeps
%modpackage jdk.jdi
%modpackage jdk.jdwp.agent
%modpackage jdk.jfr
%modpackage jdk.jlink
%modpackage jdk.jshell
%modpackage jdk.jsobject
%modpackage jdk.jstatd
%modpackage jdk.localedata
%modpackage jdk.management.agent
%modpackage jdk.management.jfr
%modpackage jdk.management
%modpackage jdk.naming.dns
%modpackage jdk.naming.rmi
%modpackage jdk.net
%modpackage jdk.nio.mapmode
%modpackage jdk.sctp
%modpackage jdk.security.auth
%modpackage jdk.security.jgss
%modpackage jdk.unsupported.desktop
%modpackage jdk.unsupported
%modpackage jdk.xml.dom
%modpackage jdk.zipfs
