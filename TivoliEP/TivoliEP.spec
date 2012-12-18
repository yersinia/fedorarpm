# Don't try fancy stuff like debuginfo, which is useless on binary-only
# packages.
# Be sure buildpolicy set to do nothing
%define        __spec_install_post %{nil}
%define 	 debug_package %{nil} 
%define        __os_install_post /usr/lib/rpm/brp-compress
#################################
# Useful macro 
#################################
%define name	TivoliEP
%define version 4.1.1.2.0
%define release 5%{?dist}
%define prefix	/opt
%define basedir %{prefix}/Tivoli/lcf
%define confdir %{_sysconfdir}/Tivoli
%define _servicename  Tivoli_lcfd1
#################################
# Command Macro
#################################
%define __find /usr/bin/find
%define __sort  /bin/sort
%define __hostname  /bin/hostname
#################################
Name:           %{name}
Summary:       	IBM Tivoli Enteprise Monitoring System. Tivoli End Point
Version:        %{version}
Release:        %{release}
Source:         %{name}-%{version}.tgz
Source1:        %{_servicename}.init
Source2:	swdis.ini
Source3:	last.cfg
NoSource:	0
URL:            http://www.ibm.com/software/tivoli/
Group:          System Environment/Daemons
Vendor:     	IBM
License:	Commercial
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
############
# From %{_servicename}
# and other script
############
Requires:	coreutils gawk procps grep sed tar
BuildRequires:  grep sed coreutils %{__find}
Requires(post):		/sbin/chkconfig %{__perl} %{__hostname} %{__find}
Requires(preun):        /sbin/chkconfig /sbin/service
Requires(postun):	%{__rm} /sbin/service

%description
%{name} is a component of the IBM Tivoli Enteprise System that allow host's
monitoring from a central server (console).

This package for default configure %{name} to work via the 
IBM Tivoli Gateway Proxy.

%prep
rm -rf $RPM_BUILD_ROOT
%setup -q 

%build
#empty

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%{__mkdir} -p -m0755 $RPM_BUILD_ROOT%{basedir}
%{__mkdir} -p -m0755 $RPM_BUILD_ROOT%{confdir}
%{__mkdir} -p -m0755 $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d
%{__cp} -rpf opt_tivoli/lcf/* $RPM_BUILD_ROOT%{basedir}
%{__cp} -rpf etc_tivoli/* $RPM_BUILD_ROOT%{confdir}
%{__install} -m0755  %{_servicename}  $RPM_BUILD_ROOT%{basedir}
%{__install} -m0755  %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/%{_servicename}
%{__install} -m0644  %{SOURCE2} $RPM_BUILD_ROOT%{confdir}/swdis.ini
for _dir in $(%{__find} $RPM_BUILD_ROOT%{basedir}/dat/* -type d)
do
 [ -f ${_dir}/last.cfg ] && %{__install} -m0644  %{SOURCE3} ${_dir}/last.cfg
done
##############
# Added swdis
#############
%{__mkdir} -p -m0755 $RPM_BUILD_ROOT%{basedir}/swdis/1/work/nested
%{__mkdir} -p -m0755 $RPM_BUILD_ROOT%{basedir}/swdis/1/work/nested/reports
#
# Cleanup
#
%{__find} $RPM_BUILD_ROOT%{basedir} -type f  -name "lcfd.log" -exec %{__rm} -f {} \;
%{__find} $RPM_BUILD_ROOT%{basedir} -type f  -name "lcfd.pid" -exec %{__rm} -f {} \;
%{__find} $RPM_BUILD_ROOT%{basedir} -type f  -name "esix49_bck-1208442-lcf.env" -exec %{__rm} -f {} \;
# 
# Fillup Manifest
#
echo "%defattr(-,root,root,-)" > %{name}-%{version}-%{release}-filelist
%{__find} $RPM_BUILD_ROOT%{basedir} -type d -printf "%%%%dir %%p\n" | \
        %{__sed} "s^$RPM_BUILD_ROOT^^" >> %{name}-%{version}-%{release}-filelist
%{__find} $RPM_BUILD_ROOT%{basedir} -type f | \
	%{__sed} "s^$RPM_BUILD_ROOT^^" | \
        %{__grep} -v "^%{basedir}/dat/.*/last.cfg$" | \
        %{__grep} -v "^%{basedir}/dat/.*/last.dat$" | \
        %{__grep} -v "^%{basedir}/dat/.*/lcfd.st$" | \
	%{__grep} -v %{name}-%{version}-%{release}-filelist  >> %{name}-%{version}-%{release}-filelist


for _dir in $(%{__find} $RPM_BUILD_ROOT%{basedir}/dat/* -type d)
do
 [ -f ${_dir}/last.cfg ] && touch ${_dir}/last.dat
done

%{__sort} -u %{name}-%{version}-%{release}-filelist > %{name}-%{version}-%{release}-filelist.ordered
%{__mv} -f %{name}-%{version}-%{release}-filelist.ordered %{name}-%{version}-%{release}-filelist

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%{__rm} -f %{name}-%{version}-%{release}-filelist

%post 
########################################
# Register the Tivoli_lcfd1 service
########################################
/sbin/chkconfig --add %{_servicename}

##################
# lcs.machine_name 
# Full Hostname
##################
_HOSTNAME="$(%{__hostname} -s)"

[ -z "${HOSTNAME}" ] && exit 1 

_LCS_MACHINE_NAME="${_HOSTNAME}"
for _dir in $(%{__find} %{basedir}/dat/* -type d)
do
 [ -f ${_dir}/last.cfg ] && %{__perl} -i -pwe 's#^(\s*lcs\.machine_name\s*=)(.*)#$1'"${_LCS_MACHINE_NAME}"'#' ${_dir}/last.cfg || : 
done

[ -f  %{confdir}/swdis.ini ] && %{__perl} -i -pwe 's#MYHOSTNAME#'"${_LCS_MACHINE_NAME}"'#' %{confdir}/swdis.ini || :

exit 0

%preun
if [ $1 = 0 ]; then
    /sbin/service %{_servicename} stop > /dev/null 2>&1 || :
    /sbin/chkconfig --del %{_servicename}
fi
exit 0

%postun
if [ $1 = 0 ]; then
  %{__rm} -rf %{basedir}
fi
if [ $1 -ge 1 ]; then
  /sbin/service %{_servicename} condrestart >/dev/null 2>&1 || :
fi
exit 0

%files -f %{name}-%{version}-%{release}-filelist
%defattr(-,root,root,-)
%dir %{prefix}/Tivoli
%{confdir}
%config(noreplace) %verify(not mtime size md5) %{basedir}/dat/*/last.cfg
%config(noreplace) %verify(not mtime size md5) %{confdir}/swdis.ini
%ghost %attr(600,root,root)  %{basedir}/dat/*/last.dat 
%ghost %attr(644,root,root)  %{basedir}/dat/*/lcfd.st
%config %attr(0755,root,root) %{_sysconfdir}/rc.d/init.d/%{_servicename}

%changelog
* Wed Oct 29 2008 Elia Pinto <yersinia.spiros@gmail.com> 4.1.1.2.0-5.el5
- Fixup broken path in last.cfg
* Wed Oct 15 2008 Elia Pinto <yersinia.spiros@gmail.com> 4.1.1.2.0-4.el5
- Add swdis.ini to /etc/Tivoli
- Claim /opt/Tivoli and /etc/Tivoli directory ownership
- Add new last.cfg. Remove old patch
- Fix Tivoli init
- added /opt/Tivoli/swdis
* Fri Aug 11 2006 Elia Pinto <yersinia.spiros@gmail.com> 4.1.1.2.0-3.EL4
- added login_interfaces patch: set to localhost. So it can be used  with
  the gateway proxy
* Thu Aug 10 2006 Elia Pinto <yersinia.spiros@gmail.com> 4.1.1.2.0-2.EL4
 - added "true" initscript. Erase symlink.
* Tue Aug  1 2006 Elia Pinto <yersinia.spiros@gmail.com> 4.1.1.2.0-1.EL4
- Renamed the package. No obsoletes necessary 
- Added symlink and preun/post/postun on the servicenamae
- Added ghost on last.dat, lcfd.st
- Added the right dependency from the shell script
- No debuginfo produced any more
- Added chcon for proper symlinks selinux filelabel
* Thu Jul 27 2006 Elia Pinto <yersinia.spiros@gmail.com> 4.1.1.2.0-1dsss
- RPMification

