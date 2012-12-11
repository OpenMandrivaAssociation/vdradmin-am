
%define name	vdradmin-am
%define version	3.6.7
%define rel	1

# backportability
%define _localstatedir %{_var}

Summary:	Web interface for VDR
Name:		%name
Version:	%version
Release:	%mkrel %rel
Group:		Video
License:	GPL
URL:		http://andreas.vdr-developer.org/vdradmin-am/
Source:		http://andreas.vdr-developer.org/download/%name-%version.tar.bz2
Source2:	vdradmin.init
Source3:	vdradmin.sysconfig
# https://qa.mandriva.com/show_bug.cgi?id=52396
# We should probably use "use open ':locale';", but it doesn't seem to
# work if we do that, TODO: investigate
Patch0:		vdradmin-am-workaround-perl-bug.patch
# we use syslog now, no logdir needed
Patch1:		vdradmin-am-no-logdir-needed.patch
# allow pidfile in non-writable directory (we precreate the file with good perms),
# allow start with empty pidfile
Patch2:		vdradmin-am-pidfile.patch
BuildRoot:	%{_tmppath}/%{name}-buildroot
BuildArch:	noarch
BuildRequires:	perl(CGI)
BuildRequires:	perl(Locale::gettext)
BuildRequires:	perl(HTTP::Date)
BuildRequires:	vdr-devel
BuildRequires:	gettext
Requires(post):	rpm-helper
Requires(preun): rpm-helper
Requires:	vdr-common
Requires:	perl(Template::Plugin::JavaScript)
Requires:	perl(Sys::Syslog)
Provides:	vdradmin

%description
Web Interface for Video Disk Recorder. With this you can manage your
recordings, timers, etc. You can also create auto-timers to record
specific programs automatically.

%prep
%setup -q
%apply_patches

rm -rf locale/*

# Setup default config
# Now using syslog: sed -i -e '/^$CONFIG{LOGFILE}\s*=\s*".*";/s,".*","vdradmin/vdradmind.log",' vdradmind.pl
#sed -i -e '/^$CONFIG{LOCAL_NET}\s*=\s*".*";/s,".*","127.0.0.1/32",' vdradmind.pl
sed -i -e '/^$CONFIG{VIDEODIR}\s*=\s*".*";/s,".*","%{_vdr_videodir}",' vdradmind.pl
sed -i -e '/^$CONFIG{VDRCONFDIR}\s*=\s*".*";/s,".*","%{_vdr_cfgdir}",' vdradmind.pl
#sed -i -e '/^$CONFIG{VDRVFAT}\s*=\s*[01];/s,[01],0,' vdradmind.pl
sed -i -e '/^\s*$PIDFILE\s*=\s*".*";/s,".*","%{_var}/run/vdradmind.pid",' vdradmind.pl
sed -i -e '/^my $SEARCH_FILES_IN_SYSTEM\s*=\s*[01];/s,[01],1,' vdradmind.pl

./vdradmind.pl --cfgdir . --config < /dev/null

cat > README.install.urpmi <<EOF
Use "vdradmind.pl --config" to configure the credentials and the tcp port.
EOF

chmod a+r README*

%build
./make.sh po

%install
rm -rf %{buildroot}

install -d -m755 %{buildroot}%{_bindir}
# symlink
cp -a vdradmind %{buildroot}%{_bindir}
install -m755 *.pl %{buildroot}%{_bindir}

install -d -m755 %{buildroot}%{_sysconfdir}
install -d -m755 %{buildroot}%{_localstatedir}/lib/vdradmin
install -m644 vdradmind.conf %{buildroot}%{_localstatedir}/lib/vdradmin
ln -s %{_localstatedir}/lib/vdradmin %{buildroot}%{_sysconfdir}/vdradmin

install -d -m755 %{buildroot}%{_sysconfdir}/sysconfig
install -m644 %SOURCE3 %{buildroot}%{_sysconfdir}/sysconfig/vdradmin

install -d -m755 %{buildroot}%{_mandir}/man1
install -m644 vdradmind.pl.1 %{buildroot}%{_mandir}/man1

install -d -m755 %{buildroot}%{_datadir}/vdradmin
cp -a template %{buildroot}%{_datadir}/vdradmin
cp -a locale %{buildroot}%{_datadir}

install -d -m755 %{buildroot}%{_initrddir}
install -m755 %SOURCE2 %{buildroot}%{_initrddir}/vdradmin

install -d -m755 %{buildroot}%{_var}/cache/vdradmin

%find_lang vdradmin

# having encoding in %lang does not work correctly
sed -i 's,\.UTF-8),),' vdradmin.lang

%clean
rm -rf %{buildroot}

%post
%_post_service vdradmin

%preun
%_preun_service vdradmin

%files -f vdradmin.lang
%defattr(-,root,root)
%doc CREDITS FAQ HISTORY INSTALL README.* contrib
%doc README.install.urpmi
%{_sysconfdir}/vdradmin
%attr(-,vdr,vdr) %dir %{_localstatedir}/lib/vdradmin
%attr(-,vdr,vdr) %dir %{_var}/cache/vdradmin

%attr(0640,vdr,vdr) %config(noreplace) %{_localstatedir}/lib/vdradmin/vdradmind.conf
%config(noreplace) %{_sysconfdir}/sysconfig/vdradmin
%{_initrddir}/vdradmin
%{_bindir}/vdradmind
%{_bindir}/vdradmind.pl
%{_bindir}/convert.pl
%{_bindir}/autotimer2searchtimer.pl
%{_datadir}/vdradmin
%{_mandir}/man1/vdradmind.pl.1*




%changelog
* Tue Jul 20 2010 Anssi Hannula <anssi@mandriva.org> 3.6.7-1mdv2011.0
+ Revision: 555080
- new version
- drop logdir stuff, now using syslog by default
- rediff perl workaround patch
- add fixup patches for logdir and pidfile handling
- allow settings misc options in sysconfig file

* Sat Jan 02 2010 Frederik Himpe <fhimpe@mandriva.org> 3.6.5-1mdv2010.1
+ Revision: 485241
- Fix BuildRequires
- update to new version 3.6.5

* Wed Jul 22 2009 Anssi Hannula <anssi@mandriva.org> 3.6.4-2mdv2010.0
+ Revision: 398488
- rebuild .mo files in %%build
- fix %%lang entries of UTF-8 .mo files that caused the files to not be
  installed when %%_install_langs is set, as it normally is
- fix /usr/bin/vdradmind not being a symlink
- fix "service vdradmin stop" for current version; vdradmin-am now uses
  process name "vdradmind"
- workaround mdv perl-Locale-gettext bug #52396 causing non-UTF-8 output

* Sat Mar 21 2009 Anssi Hannula <anssi@mandriva.org> 3.6.4-1mdv2009.1
+ Revision: 359927
- new version

* Tue Jun 03 2008 Anssi Hannula <anssi@mandriva.org> 3.6.1-2mdv2009.0
+ Revision: 214587
- define %%_localstatedir locally for backportability
- update URL

  + Pixel <pixel@mandriva.com>
    - adapt to %%_localstatedir now being /var instead of /var/lib (#22312)

* Thu Mar 06 2008 Anssi Hannula <anssi@mandriva.org> 3.6.1-2mdv2008.1
+ Revision: 181030
- add requires on perl(Template::Plugin::JavaScript), fixes epgsearch
  integration (reported by Petri Suvila)

* Fri Feb 29 2008 Anssi Hannula <anssi@mandriva.org> 3.6.1-1mdv2008.1
+ Revision: 176883
- new version

* Thu Dec 27 2007 Anssi Hannula <anssi@mandriva.org> 3.5.3-2mdv2008.1
+ Revision: 138178
- use /var/cache/vdradmin as template cache directory and handle it
  properly (fixes the error "file error - failed to create compiled
  templates directory")

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request


* Thu Mar 01 2007 Anssi Hannula <anssi@mandriva.org> 3.5.3-1mdv2007.0
+ Revision: 130692
- 3.5.3
- provide the conversion scripts

* Sat Dec 16 2006 Anssi Hannula <anssi@mandriva.org> 3.5.2-1mdv2007.1
+ Revision: 98210
- 3.5.2

* Fri Dec 01 2006 Anssi Hannula <anssi@mandriva.org> 3.5.1-1mdv2007.1
+ Revision: 89760
- 3.5.1

* Mon Nov 27 2006 Anssi Hannula <anssi@mandriva.org> 3.5.0-1mdv2007.1
+ Revision: 87608
- 3.5.0
- Import vdradmin-am

* Sat Jul 15 2006 Anssi Hannula <anssi@mandriva.org> 3.4.6-1mdv2007.0
- 3.4.6
- fix buildrequires

* Tue Jun 20 2006 Anssi Hannula <anssi@mandriva.org> 3.4.5a-2mdv2007.0
- use _ prefix for system path macros
- protect vdradmind.conf, it contains credentials in cleartext

* Sat Jun 03 2006 Anssi Hannula <anssi@mandriva.org> 3.4.5a-1mdv2007.0
- initial Mandriva release

