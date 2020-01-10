Summary:        Web interface for VDR
Name:           vdradmin-am
Version:        3.6.7
Release:        3
Group:          Video
License:        GPL
URL:            http://andreas.vdr-developer.org/vdradmin-am/
Source:         http://andreas.vdr-developer.org/download/%{name}-%{version}.tar.bz2
Source2:        vdradmin.service
Source3:        vdradmin.sysconfig
Source4:        vdradmin-wrapper.sh
# https://qa.mandriva.com/show_bug.cgi?id=52396
# We should probably use "use open ':locale';", but it doesn't seem to
# work if we do that, TODO: investigate
Patch0:         vdradmin-am-workaround-perl-bug.patch
# we use syslog now, no logdir needed
Patch1:         vdradmin-am-no-logdir-needed.patch
# allow pidfile in non-writable directory (we precreate the file with good perms),
# allow start with empty pidfile
Patch2:         vdradmin-am-pidfile.patch
BuildArch:      noarch
BuildRequires:  perl(CGI)
BuildRequires:  perl(Locale::gettext)
BuildRequires:  perl(HTTP::Date)
BuildRequires:  perl(Shell)
BuildRequires:  vdr-devel
BuildRequires:  gettext
Requires:       vdr-common
Requires:       perl(Template::Plugin::JavaScript)
Requires:       perl(Sys::Syslog)
Provides:       vdradmin

%description
Web Interface for Video Disk Recorder. With this you can manage your
recordings, timers, etc. You can also create auto-timers to record
specific programs automatically.

%prep
%setup -q
%autopatch -p1

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
install -d -m755 %{buildroot}%{_bindir}
# symlink
cp -a vdradmind %{buildroot}%{_bindir}
install -m755 *.pl %{buildroot}%{_bindir}

install -d -m755 %{buildroot}%{_sysconfdir}
install -d -m755 %{buildroot}%{_localstatedir}/lib/vdradmin
install -m644 vdradmind.conf %{buildroot}%{_localstatedir}/lib/vdradmin
ln -s %{_localstatedir}/lib/vdradmin %{buildroot}%{_sysconfdir}/vdradmin

install -d -m755 %{buildroot}%{_sysconfdir}/sysconfig
install -m644 %{SOURCE3} %{buildroot}%{_sysconfdir}/sysconfig/vdradmin

install -d -m755 %{buildroot}%{_mandir}/man1
install -m644 vdradmind.pl.1 %{buildroot}%{_mandir}/man1

install -d -m755 %{buildroot}%{_datadir}/vdradmin
cp -a template %{buildroot}%{_datadir}/vdradmin
cp -a locale %{buildroot}%{_datadir}

install -d -m755 %{buildroot}%{_unitdir}
install -m755 %{SOURCE2} %{buildroot}%{_unitdir}/vdradmin.service

install -d -m755 %{buildroot}%{_var}/cache/vdradmin

install -m755 %{SOURCE4} %{buildroot}%{_bindir}/vdradmin-wrapper.sh

%find_lang vdradmin

# having encoding in %lang does not work correctly
sed -i 's,\.UTF-8),),' vdradmin.lang

%clean

%post
%systemd_post vdradmin

%preun
%systemd_preun vdradmin

%files -f vdradmin.lang
%doc CREDITS FAQ HISTORY INSTALL README.* contrib
%doc README.install.urpmi
%{_sysconfdir}/vdradmin
%attr(-,vdr,vdr) %dir %{_localstatedir}/lib/vdradmin
%attr(-,vdr,vdr) %dir %{_var}/cache/vdradmin

%attr(0640,vdr,vdr) %config(noreplace) %{_localstatedir}/lib/vdradmin/vdradmind.conf
%config(noreplace) %{_sysconfdir}/sysconfig/vdradmin
%{_unitdir}/vdradmin*
%{_bindir}/vdradmind
%{_bindir}/vdradmind.pl
%{_bindir}/convert.pl
%{_bindir}/autotimer2searchtimer.pl
%{_datadir}/vdradmin
%{_mandir}/man1/vdradmind.pl.1*
%{_bindir}/vdradmin-wrapper.sh
