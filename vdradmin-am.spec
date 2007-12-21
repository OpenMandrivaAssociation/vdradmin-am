
%define name	vdradmin-am
%define version	3.5.3
%define rel	1

Summary:	Web interface for VDR
Name:		%name
Version:	%version
Release:	%mkrel %rel
Group:		Video
License:	GPL
URL:		http://andreas.vdr-developer.org/en/
Source:		http://andreas.vdr-developer.org/download/%name-%version.tar.bz2
Source2:	vdradmin.init
Source3:	vdradmin.sysconfig
Source4:	vdradmin.logrotate
BuildRoot:	%{_tmppath}/%{name}-buildroot
BuildArch:	noarch
BuildRequires:	perl(CGI)
BuildRequires:	perl(Locale::gettext)
BuildRequires:	vdr-devel
Requires(post):	rpm-helper
Requires(preun): rpm-helper
Requires:	vdr-common
Provides:	vdradmin

%description
Web Interface for Video Disk Recorder. With this you can manage your
recordings, timers, etc. You can also create auto-timers to record
specific programs automatically.

%prep
%setup -q

# Setup default config
sed -i -e '/^$CONFIG{LOGFILE}\s*=\s*".*";/s,".*","vdradmin/vdradmind.log",' vdradmind.pl
#sed -i -e '/^$CONFIG{LOCAL_NET}\s*=\s*".*";/s,".*","127.0.0.1/32",' vdradmind.pl
sed -i -e '/^$CONFIG{VIDEODIR}\s*=\s*".*";/s,".*","%{_vdr_videodir}",' vdradmind.pl
sed -i -e '/^$CONFIG{VDRCONFDIR}\s*=\s*".*";/s,".*","%{_vdr_cfgdir}",' vdradmind.pl
sed -i -e '/^$CONFIG{VDRVFAT}\s*=\s*[01];/s,[01],0,' vdradmind.pl
sed -i -e '/^my $SEARCH_FILES_IN_SYSTEM\s*=\s*[01];/s,[01],1,' vdradmind.pl

./vdradmind.pl --cfgdir . --config < /dev/null

cat > README.install.urpmi <<EOF
Use "vdradmind.pl --config" to configure the credentials and the tcp port.
EOF

chmod a+r README*

%install
rm -rf %{buildroot}

install -d -m755 %{buildroot}%{_bindir}
install -m755 *.pl %{buildroot}%{_bindir}

install -d -m755 %{buildroot}%{_sysconfdir}
install -d -m755 %{buildroot}%{_localstatedir}/vdradmin
install -m644 vdradmind.conf %{buildroot}%{_localstatedir}/vdradmin
ln -s %{_localstatedir}/vdradmin %{buildroot}%{_sysconfdir}/vdradmin

install -d -m755 %{buildroot}%{_sysconfdir}/sysconfig
install -m644 %SOURCE3 %{buildroot}%{_sysconfdir}/sysconfig/vdradmin

install -d -m755 %{buildroot}%{_mandir}/man1
install -m644 vdradmind.pl.1 %{buildroot}%{_mandir}/man1

install -d -m755 %{buildroot}%{_datadir}/vdradmin
cp -a template %{buildroot}%{_datadir}/vdradmin
cp -a locale %{buildroot}%{_datadir}

install -d -m755 %{buildroot}%{_initrddir}
install -m755 %SOURCE2 %{buildroot}%{_initrddir}/vdradmin

install -d -m755 %{buildroot}%{_logdir}/vdradmin

install -d -m755 %{buildroot}%{_sysconfdir}/logrotate.d
install -m644 %SOURCE4 %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

%find_lang vdradmin

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
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%attr(-,vdr,vdr) %dir %{_localstatedir}/vdradmin
%attr(-,vdr,vdr) %dir %{_logdir}/vdradmin
%attr(0640,vdr,vdr) %config(noreplace) %{_localstatedir}/vdradmin/vdradmind.conf
%config(noreplace) %{_sysconfdir}/sysconfig/vdradmin
%{_initrddir}/vdradmin
%{_bindir}/vdradmind.pl
%{_bindir}/convert.pl
%{_bindir}/autotimer2searchtimer.pl
%{_datadir}/vdradmin
%{_mandir}/man1/vdradmind.pl.1*


