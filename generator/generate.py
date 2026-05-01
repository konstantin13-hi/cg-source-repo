import sys
import shutil
from pathlib import Path
import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent
TEMPLATE_DIR = ROOT / "templates"

def java_type(t):
    return {
        "Long": "Long",
        "String": "String",
        "Integer": "Integer",
        "Boolean": "Boolean",
        "Date": "LocalDate",
    }.get(t, t)

def lower_first(s):
    return s[0].lower() + s[1:]

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate.py artifacts/model.yaml ../generated-app-repo")
        sys.exit(1)

    model_path = Path(sys.argv[1])
    output = Path(sys.argv[2])

    with open(model_path, "r", encoding="utf-8") as f:
        model = yaml.safe_load(f)

    package = model["project"]["package"]
    package_path = Path(*package.split("."))

    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    env.filters["java_type"] = java_type
    env.filters["lower_first"] = lower_first

    app_src = output / "src" / "main" / "java" / package_path
    test_src = output / "src" / "test" / "java" / package_path
    resources = output / "src" / "main" / "resources"

    for d in [app_src / "entity", app_src / "repository", app_src / "service", app_src / "controller", test_src, resources]:
        d.mkdir(parents=True, exist_ok=True)

    # Static project files
    for name in ["pom.xml", "Dockerfile", "Jenkinsfile", "README.md"]:
        (output / name).write_text(env.get_template(name + ".j2").render(model=model, package=package), encoding="utf-8")

    (resources / "application.properties").write_text(env.get_template("application.properties.j2").render(model=model), encoding="utf-8")
    (app_src / "Application.java").write_text(env.get_template("Application.java.j2").render(package=package), encoding="utf-8")
    (test_src / "ApplicationTests.java").write_text(env.get_template("ApplicationTests.java.j2").render(package=package), encoding="utf-8")

    for entity_name, entity in model["entities"].items():
        fields = entity["fields"]
        ctx = {"package": package, "entity_name": entity_name, "fields": fields}
        (app_src / "entity" / f"{entity_name}.java").write_text(env.get_template("Entity.java.j2").render(**ctx), encoding="utf-8")
        (app_src / "repository" / f"{entity_name}Repository.java").write_text(env.get_template("Repository.java.j2").render(**ctx), encoding="utf-8")
        (app_src / "service" / f"{entity_name}Service.java").write_text(env.get_template("Service.java.j2").render(**ctx), encoding="utf-8")
        (app_src / "controller" / f"{entity_name}Controller.java").write_text(env.get_template("Controller.java.j2").render(**ctx), encoding="utf-8")

    print(f"Generated application in: {output}")

if __name__ == "__main__":
    main()
