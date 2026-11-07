Name:		jboss-logging
Version:	3.6.3.Final
Release:	1
Summary:	JBoss Logging facade
Group:		Development/Java
License:	ASL 2.0
URL:		https://github.com/jboss-logging/jboss-logging
Source0:	https://github.com/jboss-logging/jboss-logging/archive/refs/tags/v%{version}.tar.gz#/jboss-logging-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	python
# The published POMs name these parents, and the RPMs do not require them.
BuildRequires:	mvn(org.jboss:jboss-parent:pom::)
BuildRequires:	mvn(org.slf4j:slf4j-parent:pom::)
BuildRequires:	mvn(org.slf4j:slf4j-api)
BuildRequires:	mvn(log4j:log4j)
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildSystem:	maven

Obsoletes:	%{name}-javadoc < %{version}

%description
Logging facade used by JBoss projects. 3.6.3.Final is the current
release. This build keeps the JDK, SLF4J 1.7 and Log4j 1.2 providers.
Log4j 2 and JBoss Log Manager are not system jars, so those providers
are left out. The automatic module name is org.jboss.logging. Tests
are skipped.

%prep
%autosetup -n jboss-logging-%{version}
python - <<'PY'
import xml.etree.ElementTree as ET
from pathlib import Path

NS = "http://maven.apache.org/POM/4.0.0"
ET.register_namespace("", NS)
ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")

def local(tag):
    return tag.rsplit("}", 1)[-1]

def artifact_of(elem):
    for item in elem:
        if local(item.tag) == "artifactId":
            return (item.text or "").strip()
    return ""

drop_deps = {
    "jboss-logmanager",
    "log4j-api",
    "log4j-core",
    "junit-jupiter",
    "junit-bom",
    "logback-classic",
}
drop_plugins = {
    "formatter-maven-plugin",
    "impsort-maven-plugin",
    "maven-source-plugin",
    "maven-surefire-plugin",
    "maven-javadoc-plugin",
    "maven-bundle-plugin",
    "module-info",
}
tree = ET.parse("pom.xml")
root = tree.getroot()
removed = []
for parent in list(root.iter()):
    for child in list(parent):
        kind = local(child.tag)
        art = artifact_of(child)
        if kind == "dependency" and art in drop_deps:
            parent.remove(child)
            removed.append(art)
        elif kind == "plugin" and art in drop_plugins:
            parent.remove(child)
            removed.append(art)
missing = (drop_deps | drop_plugins) - set(removed)
if missing:
    raise SystemExit("not removed " + " ".join(sorted(missing)))
parent_ver = None
for child in list(root):
    if local(child.tag) != "parent":
        continue
    for item in child:
        if local(item.tag) == "version":
            parent_ver = item
if parent_ver is None or (parent_ver.text or "").strip() != "52":
    raise SystemExit("unexpected parent version")
parent_ver.text = "55"
tag = "{" + NS + "}version"
for plugin in root.iter():
    if local(plugin.tag) != "plugin" or artifact_of(plugin) != "maven-compiler-plugin":
        continue
    if any(local(item.tag) == "version" for item in plugin):
        raise SystemExit("compiler already versioned")
    art = None
    for item in list(plugin):
        if local(item.tag) == "artifactId":
            art = item
    node = ET.Element(tag)
    node.text = "3.12.1"
    plugin.insert(list(plugin).index(art) + 1, node)
tree.write("pom.xml", encoding="UTF-8", xml_declaration=True)
text = Path("pom.xml").read_text(encoding="utf-8")
for art in sorted(drop_deps | drop_plugins):
    if "<artifactId>" + art + "</artifactId>" in text:
        raise SystemExit("survived " + art)
if "<version>55</version>" not in text:
    raise SystemExit("parent 55 missing")
if "<artifactId>log4j</artifactId>" not in text or "<artifactId>slf4j-api</artifactId>" not in text:
    raise SystemExit("slf4j or log4j dependency missing")

java = Path("src/main/java/org/jboss/logging")
for name in (
    "JBossLogManagerLogger.java",
    "JBossLogManagerProvider.java",
    "Log4j2Logger.java",
    "Log4j2LoggerProvider.java",
):
    path = java / name
    if not path.is_file():
        raise SystemExit("missing " + name)
    path.unlink()
prov_path = java / "LoggerProviders.java"
prov = prov_path.read_text(encoding="utf-8")
old_if = (
    '                if ("jboss".equalsIgnoreCase(loggerProvider)) {\n'
    '                    return tryJBossLogManager(cl, "system property");\n'
    '                } else if ("jdk".equalsIgnoreCase(loggerProvider)) {\n'
    '                    return tryJDK("system property");\n'
    '                } else if ("log4j2".equalsIgnoreCase(loggerProvider)) {\n'
    '                    return tryLog4j2(cl, "system property");\n'
    '                } else if ("log4j".equalsIgnoreCase(loggerProvider)) {'
)
new_if = (
    '                if ("jdk".equalsIgnoreCase(loggerProvider)) {\n'
    '                    return tryJDK("system property");\n'
    '                } else if ("log4j".equalsIgnoreCase(loggerProvider)) {'
)
old_search = (
    "        try {\n"
    "            return tryJBossLogManager(cl, null);\n"
    "        } catch (Throwable t) {\n"
    "            // nope...\n"
    "        }\n"
    "        try {\n"
    "            return tryLog4j2(cl, null);\n"
    "        } catch (Throwable t) {\n"
    "            // nope...\n"
    "        }\n"
)
if prov.count(old_if) != 1 or prov.count(old_search) != 1:
    raise SystemExit("provider selector did not match")
prov = prov.replace(old_if, new_if).replace(old_search, "")
prov = prov.replace("import java.util.logging.LogManager;\n", "")

def drop_method(body, name):
    token = "private static LoggerProvider " + name + "("
    start = body.find(token)
    if start < 0:
        raise SystemExit("method missing " + name)
    line_start = body.rfind("\n", 0, start) + 1
    prev = body.rfind("\n", 0, line_start - 1) + 1
    if body[prev:line_start].lstrip().startswith("//"):
        line_start = prev
    brace = body.find("{", start)
    depth = 0
    i = brace
    while i < len(body):
        if body[i] == "{":
            depth += 1
        elif body[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                if end < len(body) and body[end] == "\n":
                    end += 1
                return body[:line_start] + body[end:]
        i += 1
    raise SystemExit("brace mismatch " + name)

prov = drop_method(prov, "tryLog4j2")
prov = drop_method(prov, "tryJBossLogManager")
for banned in ("tryLog4j2", "tryJBossLogManager", "Log4j2Logger", "JBossLogManagerProvider"):
    if banned in prov:
        raise SystemExit("provider still mentions " + banned)
if "tryLog4j(" not in prov or "trySlf4j(" not in prov or "tryJDK(" not in prov:
    raise SystemExit("kept provider missing")
prov_path.write_text(prov, encoding="utf-8")
PY

%build -a
printf 'Automatic-Module-Name: org.jboss.logging\n' > target/auto-module.mf
jar ufm target/jboss-logging-%{version}.jar target/auto-module.mf
java --module-path target/jboss-logging-%{version}.jar --describe-module org.jboss.logging | grep -q '^org.jboss.logging'

%files -f .mfiles
%doc LICENSE.txt README.adoc
