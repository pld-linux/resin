Summary:	A fast servlet and JSP engine
Summary(pl):	Szybki silnik servletów i JSP
Name:		resin
Version:	1.2.1
Release:	2
License:	Caucho Developer Source License
Group:		Networking/Daemons
Source0:	http://www.caucho.com/download/%{name}-%{version}.tar.gz
Source1:	%{name}.conf
Source2:	%{name}.init
Source3:	%{name}.sysconfig
Patch0:		%{name}-configure-test-httpd.conf.patch
URL:		http://www.caucho.com/
# Provides:	httpd
# Provides:	webserver
Provides:	jsp, servlet
Prereq:		/sbin/chkconfig
Prereq:		%{_sbindir}/apxs
BuildRequires:	apache-devel
Requires:	apache
Requires:	apache(EAPI)
# rather necessary, but does it matter if pld doesn't contain any? ;-)
# BuildRequires:	jdk >= 1.2
# for running even kaffe should be enough, since it's java 1.1
Requires:	jre >= 1.1
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Resin is a fast servlet and JSP engine supporting load balancing for
increased reliability. Resin encourages separation of content from
style with its XSL support. Servlets can generate simple XML and use
an XSL filter to format results for each client's capability, from
palm pilots to Mozilla.

%description -l pl
Resin to szybki silnik servletowy i JSP, obs³uguj±cy load balancing
aby osi±gn±æ wiêksz± niezawodno¶æ. Resin wspiera oddzielenie tre¶ci od
stylu poprzez obs³ugê XSL. Servlety mog± generowaæ prosy XML i u¿ywaæ
filtra XSL do formatowania wyników zale¿nie od mo¿liwo¶ci klienta, od
Palm Pilotów do Mozilli.

%define		_libexecdir	%{_prefix}/lib/apache

%prep
%setup -q -n %{name}%{version}
%patch0 -p1

%build
#aclocal
#autoconf
#cp -f /usr/share/automake/config.* .
%configure2_13 \
	--with-apache
# should be found depending on location of `java' binary
# and/or JAVA_HOME
#	 --with-java-home=%{_libdir}/java \

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_libexecdir} \
	  $RPM_BUILD_ROOT%{_sysconfdir}/{httpd,rc.d/init.d,sysconfig} \
	  $RPM_BUILD_ROOT%{_datadir}/resin/{bin,lib,conf} \
	  $RPM_BUILD_ROOT/home/httpd/resin/WEB-INF \
	  $RPM_BUILD_ROOT/var/{run,log}/resin \
	  $RPM_BUILD_ROOT/var/lib/resin/{cache,work}

cp -R bin lib xsl $RPM_BUILD_ROOT%{_datadir}/resin
cp -R doc/*  $RPM_BUILD_ROOT/home/httpd/resin

# unfortunately a http user has no permissions in %{_sysconfdir}/httpd,
# so resin.init has to use a different (default) directory :-/
install %{SOURCE1} $RPM_BUILD_ROOT%{_datadir}/resin/conf
ln -sf %{_datadir}/resin/conf/resin.conf $RPM_BUILD_ROOT%{_sysconfdir}/httpd

install src/c/plugin/apache/mod_caucho.so $RPM_BUILD_ROOT/%{_libexecdir}
install src/c/plugin/resin/resin $RPM_BUILD_ROOT%{_datadir}/resin/bin
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/resin
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/resin

gzip -9nf LICENSE readme.txt conf/samples/*

%clean
rm -rf $RPM_BUILD_ROOT

%preun
if [ "$1" = "0" ]; then
	%{_sbindir}/apxs -e -A -n caucho %{_libexecdir}/mod_caucho.so 1>&2
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
	if [ -f /var/lock/subsys/resin ]; then
		/etc/rc.d/init.d/resin stop 1>&2
	fi
	/sbin/chkconfig --del resin
fi

%post
/sbin/chkconfig --add resin
%{_sbindir}/apxs -e -a -n caucho %{_libexecdir}/mod_caucho.so 1>&2
if [ -f /var/lock/subsys/httpd ]; then
	if [ -f /var/lock/subsys/resin ]; then
		/etc/rc.d/init.d/resin restart 1>&2
	else
		echo "Run \"/etc/rc.d/init.d/resin start\" to start resin daemon."
	fi
	/etc/rc.d/init.d/httpd restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/resin start\" to start resin daemon."
	echo "Run \"/etc/rc.d/init.d/httpd start\" to start apache http daemon."
fi

%files
%defattr(644,root,root,755)
%doc LICENSE.gz readme.txt.gz conf/samples/*gz

%attr(0660,root,http) %config(noreplace) %verify(not size mtime md5) %{_datadir}/resin/conf/resin.conf
%attr(0640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/httpd/resin.conf
%attr(0640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/sysconfig/resin
%attr(754,root,root) /etc/rc.d/init.d/resin

%attr(0755,root,root) %{_libexecdir}/mod_caucho.so

%dir %{_datadir}/resin
%dir %{_datadir}/resin/bin
%attr(0755,root,root) %{_datadir}/resin/bin/*
%dir %{_datadir}/resin/lib
%dir %{_datadir}/resin/xsl
%{_datadir}/resin/lib/*
%{_datadir}/resin/xsl/*

%dir /var/lib/resin
%attr(0770,root,http) /var/lib/resin/*
%attr(0770,root,http) %dir /var/log/resin
%attr(0770,root,http) %dir /var/run/resin

%dir /home/httpd/resin
%attr(0770,root,http) %dir /home/httpd/resin/WEB-INF
%dir /home/httpd/resin/examples
%dir /home/httpd/resin/images
%dir /home/httpd/resin/javadoc
%dir /home/httpd/resin/java_tut
%dir /home/httpd/resin/ref
%dir /home/httpd/resin/css
/home/httpd/resin/examples/*
/home/httpd/resin/images/*
/home/httpd/resin/javadoc/*
/home/httpd/resin/java_tut/*
/home/httpd/resin/ref/*
/home/httpd/resin/*.xtp
/home/httpd/resin/toc.xml
