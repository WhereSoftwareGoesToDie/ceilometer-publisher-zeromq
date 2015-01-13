Name:           ceilometer-publisher-rabbitmq
Version:        0.0.5
Release:        0anchor2%{?dist}
Group:          Development/Libraries
Summary:        A publisher plugin for Ceilometer that outputs to RabbitMQ
License:        Apache
URL:            https://github.com/anchor/ceilometer-publisher-rabbitmq
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  python
BuildRequires:  python-setuptools
BuildRequires:  python-pip
Requires:       python-pika

%description
A publisher plugin for Ceilometer that outputs to RabbitMQ.

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

* Tue Jan 06 2015 Barney Desmond <barney.desmond@anchor.net.au> - 0.0.5-0anchor2
- Add some install notes
- Fix runtime dependency

* Mon Dec 01 2014 Oswyn Brent <oswyn.brent@anchor.com.au> - 0.0.5-0anchor1
- Reconnect on disconnect

* Tue Nov 11 2014 Oswyn Brent <oswyn.brent@anchor.com.au> - 0.0.3-0anchor1
- Initial build
