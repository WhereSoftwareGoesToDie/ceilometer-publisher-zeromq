Name:           ceilometer-publisher-zeromq
Version:        0.0.4
Release:        0anchor1%{?dist}
Group:          Development/Libraries
Summary:        A publisher plugin for Ceilometer that outputs to a collector via ZeroMQ
License:        Apache
URL:            https://github.com/anchor/ceilometer-publisher-zeromq
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  python
BuildRequires:  python-setuptools
BuildRequires:  python-pip
Requires:       python-zmq

%description
A publisher plugin for Ceilometer that outputs to a collector via ZeroMQ.

%prep
%setup -n %{name}-%{version}

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root %{buildroot} --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)

%changelog

* Tue Mar 09 2015 Sharif Olorin <sio@tesser.org> - 0.0.4-0anchor1
- Add mutex around ZMQ sends

* Mon Mar 09 2015 Oswyn Brent <oswyn.brent@anchor.com.au> - 0.0.3-0anchor1
- Publisher now uses an internal buffer to avoid race conditions

* Tue Mar 03 2015 Sharif Olorin <sio@tesser.org> - 0.0.2-0anchor1
- Renamed publisher with distinct name from old publisher

* Wed Feb 25 2015 Oswyn Brent <oswyn.brent@anchor.com.au> - 0.0.1-0anchor1
- Initial build
