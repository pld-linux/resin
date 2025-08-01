
# TODO:
#   - test the Apache module
#   - review by PLD Java and Apache specialists

%define		apxs		/usr/sbin/apxs
%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR)
Summary:	A fast servlet and JSP engine
Summary(pl.UTF-8):	Szybki silnik servletów i JSP
Name:		resin
Version:	3.0.13
Release:	0.1
License:	GPL
Group:		Networking/Daemons
Source0:	http://www.caucho.com/download/%{name}-%{version}.tar.gz
# Source0-md5:	4e5a07b29b6b8ed86630c169bf62aba2
Source1:	%{name}-mod_caucho.conf
Source2:	%{name}.init
Source3:	%{name}.sysconfig
Patch0:		%{name}-configure-test-httpd.conf.patch
Patch1:		%{name}-apache2-test.patch
Patch2:		%{name}-paths.patch
URL:		http://www.caucho.com/resin/
BuildRequires:	apache-devel
BuildRequires:	jdk >= 1.2
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
# for running even kaffe should be enough, since it's java 1.1
Requires:	jre >= 1.1
# Provides:	webserver
Provides:	group(http)
Provides:	jsp
Provides:	servlet
Provides:	user(http)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Resin is a fast servlet and JSP engine supporting load balancing for
increased reliability. Resin encourages separation of content from
style with its XSL support. Servlets can generate simple XML and use
an XSL filter to format results for each client's capability, from
palm pilots to Mozilla.

This package provides the standalone Resin webserver only. Install
"apache-mod_caucho" package to use Resin with apache.

%description -l pl.UTF-8
Resin to szybki silnik servletowy i JSP, obsługujący load balancing
aby osiągnąć większą niezawodność. Resin wspiera oddzielenie treści od
stylu poprzez obsługę XSL-a. Servlety mogą generować prosty XML i
używać filtra XSL do formatowania wyników zależnie od możliwości
klienta, od Palm Pilotów do Mozilli.

Ten pakiet zawiera jedynie samodzielny serwer WWW Resina. Aby użyć
Resin z Apache należy zainstalować dodatkowo pakiet
"apache-mod_caucho".

%package -n apache-mod_caucho
Summary:	An Apache module for Resin servlet and JSP engine
Summary(pl.UTF-8):	Moduł Apache dla silnika servletów i JSP
Group:		Networking/Daemons
Requires(post,preun):	/usr/sbin/apxs
Requires:	apache
Requires:	resin = %{epoch}:%{version}-%{release}

%description -n apache-mod_caucho
An Apache module for Resin servlet and JSP engine.

%description -n apache-mod_caucho -l pl.UTF-8
Moduł Apache dla silnika servletów i JSP.

%package doc
Summary:	Resin online documentation
Summary(pl.UTF-8):	Dokumentacja online dla Resina
Group:		Networking/Daemons
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description doc
Provides Resin documentation as http://localhost:8080/resin-doc/
(assuming default Resin configuration).

%description doc -l pl.UTF-8
Udostępnia dokumentację Resina jako http://localhost:8080/resin-doc/
(zakładając domyślną konfigurację Resina).

%prep
%setup -q
%patch -P0 -p1
%patch -P1 -p1
%patch -P2 -p1

%build
# this are available in the -src tarball only, which is harder to build
#rm -f configure # to get permissions right
#aclocal
#autoconf

cp -f /usr/share/automake/config.* automake
%configure \
	--with-apxs=%{_sbindir}/apxs \
	--with-apache \
	--with-jni-include="-I/usr/%{_lib}/java/include -I/usr/%{_lib}/java/include/linux" \
	CFLAGS="%{rpmcflags} `/usr/bin/apr-1-config --includes --cppflags` `/usr/bin/apu-1-config --includes`"
# should be found depending on location of `java' binary
# and/or JAVA_HOME
#	 --with-java-home=%{_libdir}/java \

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_pkglibdir} \
	  $RPM_BUILD_ROOT%{_sysconfdir}/{resin,httpd/httpd.conf,rc.d/init.d,sysconfig} \
	  $RPM_BUILD_ROOT%{_datadir}/resin/{lib,bin,webapps} \
	  $RPM_BUILD_ROOT%{_libdir}/resin \
	  $RPM_BUILD_ROOT/var/{run,log}/resin \
	  $RPM_BUILD_ROOT/var/lib/resin/{cache,work,tmp,webapps}

libtool --mode=install install modules/c/src/apache2/mod_caucho.la $RPM_BUILD_ROOT%{_pkglibdir}/wtf

cp -R bin/*{.sh,.pl} $RPM_BUILD_ROOT%{_datadir}/resin/bin
cp -R conf/* $RPM_BUILD_ROOT%{_sysconfdir}/resin
cp -R lib/* $RPM_BUILD_ROOT%{_datadir}/resin/lib
cp -R webapps/* $RPM_BUILD_ROOT%{_datadir}/resin/webapps

install modules/c/src/resin_os/libresin_os.so $RPM_BUILD_ROOT%{_libdir}/resin

install %{SOURCE1} $RPM_BUILD_ROOT/etc/httpd/httpd.conf/70_mod_caucho.conf
install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/resin
install %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/resin

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 51 http
%useradd -u 51 -r -d /home/services/httpd -s /bin/false -c "HTTP User" -g http http

%postun
if [ "$1" = "0" ]; then
	%userremove http
	%groupremove http
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/resin ]; then
		/etc/rc.d/init.d/resin stop 1>&2
	fi
	/sbin/chkconfig --del resin
fi

%post
/sbin/chkconfig --add resin
if [ -f /var/lock/subsys/resin ]; then
	/etc/rc.d/init.d/resin restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/resin start\" to start resin daemon."
fi

%preun -n apache-mod_caucho
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
fi

%post -n apache-mod_caucho
if [ -f /var/lock/subsys/httpd ]; then
	/etc/rc.d/init.d/httpd restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/httpd start\" to start apache HTTP daemon."
fi

%post doc
if [ -f /var/lock/subsys/resin ]; then
	/etc/rc.d/init.d/resin restart 1>&2
fi

%postun doc
if [ -f /var/lock/subsys/resin ]; then
	/etc/rc.d/init.d/resin restart 1>&2
	rm -f /var/lib/resin/webapps/resin-doc 2>/dev/null
fi


%files
%defattr(644,root,root,755)
%doc README
%attr(660,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/resin/*
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/resin
%attr(754,root,root) /etc/rc.d/init.d/resin

%dir %{_libdir}/resin
%attr(755,root,root) %{_libdir}/resin/*

%dir %{_datadir}/resin
%dir %{_datadir}/resin/bin
%attr(755,root,root) %{_datadir}/resin/bin/*
%dir %{_datadir}/resin/lib
%{_datadir}/resin/lib/*
%dir %{_datadir}/resin/webapps
%{_datadir}/resin/webapps/ROOT

%dir /var/lib/resin
%attr(770,root,http) /var/lib/resin/*
%attr(770,root,http) %dir /var/log/resin
%attr(770,root,http) %dir /var/run/resin

%files -n apache-mod_caucho
%defattr(644,root,root,755)
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/httpd/httpd.conf/70_mod_caucho.conf
%attr(755,root,root) %{_pkglibdir}/mod_caucho.so

%files doc
%defattr(644,root,root,755)
%{_datadir}/resin/webapps/resin-doc*
