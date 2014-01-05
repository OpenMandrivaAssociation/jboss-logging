%{?_javapackages_macros:%_javapackages_macros}
%global namedreltag .GA
%global namedversion %{version}%{?namedreltag}

Name:             jboss-logging
Version:          3.1.3
Release:          2.0%{?dist}
Summary:          The JBoss Logging Framework
License:          ASL 2.0
URL:              https://github.com/jboss-logging/jboss-logging
Source0:          https://github.com/jboss-logging/jboss-logging/archive/%{namedversion}.tar.gz

BuildArch:        noarch

BuildRequires:    maven-local
BuildRequires:    maven-compiler-plugin
BuildRequires:    maven-install-plugin
BuildRequires:    maven-jar-plugin
BuildRequires:    maven-javadoc-plugin
BuildRequires:    maven-release-plugin
BuildRequires:    maven-resources-plugin
BuildRequires:    maven-surefire-plugin
BuildRequires:    maven-enforcer-plugin
BuildRequires:    jboss-logmanager
BuildRequires:    slf4j
BuildRequires:    log4j
BuildRequires:    apiviz
BuildRequires:    jboss-parent
BuildRequires:    maven-surefire-provider-junit

%description
This package contains the JBoss Logging Framework.

%package javadoc
Summary:          Javadocs for %{name}

%description javadoc
This package contains the API documentation for %{name}.

%prep
%setup -q -n jboss-logging-%{namedversion}

%build
%mvn_build -f

%install
%mvn_install

%files -f .mfiles
%doc src/main/resources/META-INF/LICENSE.txt

%files javadoc -f .mfiles-javadoc
%doc src/main/resources/META-INF/LICENSE.txt

%changelog
* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Jun 28 2013 Marek Goldmann <mgoldman@redhat.com> - 3.1.3-1
- Upstream release 3.1.3.GA

* Tue Feb 26 2013 Marek Goldmann <mgoldman@redhat.com> - 3.1.2-1
- Upstream release 3.1.2.GA
- Move to mvn_build and mvn_install macros
- License change to ASL 2.0

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 3.1.0-5
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Fri Jul 20 2012 Marek Goldmann <mgoldman@redhat.com> - 3.1.0-4
- Fixed BR

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sun Feb 26 2012 Marek Goldmann <mgoldman@redhat.com> 3.1.0-2
- Release bump

* Sun Feb 26 2012 Marek Goldmann <mgoldman@redhat.com> 3.1.0-1
- Upstream release 3.1.0.GA
- Relocated jars to _javadir

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.0-0.2.CR1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Nov 18 2011 Marek Goldmann <mgoldman@redhat.com> 3.1.0-0.1.CR1
- Upstream release 3.1.0.CR1

* Mon Sep 19 2011 Marek Goldmann <mgoldman@redhat.com> 3.0.1-1
- Upstream release 3.0.1.GA

* Thu Jul 28 2011 Marek Goldmann <mgoldman@redhat.com> 3.0.0-1
- Initial packaging

