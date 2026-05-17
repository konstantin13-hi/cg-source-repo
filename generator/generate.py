import sys
from pathlib import Path
import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent
TEMPLATE_DIR = ROOT / "templates"

DEFAULT_OPERATIONS = {"read", "create", "delete"}


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


def load_usecases(model_path: Path):
    """Load optional artifacts/usecases.yaml placed next to model.yaml.

    If the file does not exist, the generator keeps the Version 1 behavior
    and generates the default CRUD subset: read, create, delete.
    """
    usecases_path = model_path.parent / "usecases.yaml"
    if not usecases_path.exists():
        return {}

    with open(usecases_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    operations_by_entity = {}
    for usecase in data.get("useCases", []):
        entity = usecase.get("entity")
        operation = usecase.get("operation")
        if not entity or not operation:
            continue
        operations_by_entity.setdefault(entity, set()).add(operation)

    return operations_by_entity


def main():
    if len(sys.argv) != 3:
        print("Usage: python generate.py artifacts/model.yaml ../generated-app-repo")
        sys.exit(1)

    model_path = Path(sys.argv[1])
    output = Path(sys.argv[2])

    with open(model_path, "r", encoding="utf-8") as f:
        model = yaml.safe_load(f)

    usecase_operations = load_usecases(model_path)

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

    for name in ["pom.xml", "Dockerfile", "Jenkinsfile", "README.md"]:
        (output / name).write_text(env.get_template(name + ".j2").render(model=model, package=package), encoding="utf-8")

    (resources / "application.properties").write_text(env.get_template("application.properties.j2").render(model=model), encoding="utf-8")
    (app_src / "Application.java").write_text(env.get_template("Application.java.j2").render(package=package), encoding="utf-8")
    (test_src / "ApplicationTests.java").write_text(env.get_template("ApplicationTests.java.j2").render(package=package), encoding="utf-8")

    for entity_name, entity in model["entities"].items():
        fields = entity["fields"]
        relations = entity.get("relations", [])

        # If usecases.yaml defines operations for an entity, use them.
        # Otherwise keep default Version 1 behavior.
        operations = usecase_operations.get(entity_name, DEFAULT_OPERATIONS)

        ctx = {
            "package": package,
            "entity_name": entity_name,
            "fields": fields,
            "relations": relations,
            "operations": operations,
        }

        (app_src / "entity" / f"{entity_name}.java").write_text(env.get_template("Entity.java.j2").render(**ctx), encoding="utf-8")
        (app_src / "repository" / f"{entity_name}Repository.java").write_text(env.get_template("Repository.java.j2").render(**ctx), encoding="utf-8")
        (app_src / "service" / f"{entity_name}Service.java").write_text(env.get_template("Service.java.j2").render(**ctx), encoding="utf-8")
        (app_src / "controller" / f"{entity_name}Controller.java").write_text(env.get_template("Controller.java.j2").render(**ctx), encoding="utf-8")

    print(f"Generated application in: {output}")


if __name__ == "__main__":
    main()
