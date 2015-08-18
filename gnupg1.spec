Summary: A stripped-down version of gnupg version 1
Name: gnupg1
Version: 1.4.11
Release: 3%{?dist}
License: GPLv3+ with exceptions
Group: Applications/System
Source0: ftp://ftp.gnupg.org/gcrypt/gnupg/gnupg-%{version}.tar.bz2
Source1: ftp://ftp.gnupg.org/gcrypt/gnupg/gnupg-%{version}.tar.bz2.sig
Source2: gnupg-shm-coprocessing.expect
Patch0: gnupg-1.4.1-gcc.patch
URL: http://www.gnupg.org/
# Requires autoconf >= 2.60 because earlier autoconf didn't define $localedir.
BuildRequires: autoconf >= 2.60
BuildRequires: automake, bzip2-devel, expect, ncurses-devel
BuildRequires: openldap-devel, readline-devel, zlib-devel, gettext-devel
BuildRequires: curl-devel
%ifnarch s390 s390x
BuildRequires: libusb-devel
%endif
# pgp-tools, perl-GnuPG-Interface include 'Requires: gpg' -- Rex
Provides: gpg = %{version}-%{release}
Requires(post): /sbin/install-info
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
GnuPG (GNU Privacy Guard) is a GNU utility for encrypting data and
creating digital signatures. GnuPG has advanced key management
capabilities and is compliant with the proposed OpenPGP Internet
standard described in RFC2440. Since GnuPG doesn't use any patented
algorithm, it is not compatible with any version of PGP2 (PGP2.x uses
only IDEA for symmetric-key encryption, which is patented worldwide).

This is a stripped down version, provided only to make it possible to work
around https://bugzilla.redhat.com/show_bug.cgi?id=637902 .

%prep
%setup -q -n gnupg-%{version}
%patch0 -p1 -b .gcc

# Convert these files to UTF-8, per rpmlint.
iconv -f koi8-ru -t utf-8 doc/gpg.ru.1 > doc/gpg.ru.utf8.1
mv doc/gpg.ru.utf8.1 doc/gpg.ru.1
iconv -f iso-8859-15 -t utf-8 THANKS > THANKS.utf8
mv THANKS.utf8 THANKS

autoreconf

%build
configure_flags=

%ifarch ppc64 sparc64
configure_flags=--disable-asm
%endif
CFLAGS="$RPM_OPT_FLAGS -fPIE -DPIC" ; export CFLAGS
LDFLAGS="$RPM_OPT_FLAGS -pie -Wl,-z,relro,-z,now" ; export LDFLAGS
%configure \
    --disable-rpath \
    --with-zlib --enable-noexecstack \
    $configure_flags
make %{?_smp_mflags}
env LANG=C expect -f %{SOURCE2}

%check
make check

%clean
rm -rf %{buildroot}

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
mv %{buildroot}%{_bindir}/gpg{,1}
mv %{buildroot}%{_mandir}/man1/gpg{,1}.1
install -m644 doc/gnupg1.info %{buildroot}/%{_infodir}
rm -f %{buildroot}/%{_infodir}/dir
%find_lang gnupg

%post
if test -s %{_infodir}/gnupg1.info.gz ; then
    /sbin/install-info %{_infodir}/gnupg1.info.gz %{_infodir}/dir 2> /dev/null
fi
exit 0

%preun
if [ $1 = 0 ]; then
    if test -s %{_infodir}/gnupg1.info.gz ; then
        /sbin/install-info --delete %{_infodir}/gnupg1.info.gz %{_infodir}/dir 2> /dev/null
    fi
fi
exit 0

%files -f gnupg.lang
%defattr(-,root,root)
%doc AUTHORS BUGS COPYING INSTALL NEWS PROJECTS README THANKS TODO
%doc doc/DETAILS doc/HACKING doc/OpenPGP doc/samplekeys.asc
%{_bindir}/gpg1
%exclude %{_bindir}/gpg-zip
%exclude %{_bindir}/gpgsplit
%exclude %{_bindir}/gpgv
%exclude %{_libexecdir}/gnupg
%{_datadir}/gnupg
%{_infodir}/gnupg1.info.gz
%exclude %{_mandir}/man1/gpg-zip.1.gz
%{_mandir}/man1/gpg1.1.gz
%exclude %{_mandir}/man1/gpg.ru.1.gz
%exclude %{_mandir}/man1/gpgv.1.gz
%{_mandir}/man7/gnupg.7.gz

%changelog
* Tue May 31 2011 Miloslav Trmač <mitr@redhat.com> - 1.4.11-3
- Initial release, stripped down from rawhide packaging
