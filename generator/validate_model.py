import sys
import yaml

def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_model.py artifacts/model.yaml")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        model = yaml.safe_load(f)

    assert "project" in model, "Missing project section"
    assert "entities" in model, "Missing entities section"

    for entity_name, entity in model["entities"].items():
        assert "fields" in entity, f"Missing fields in {entity_name}"
        assert "id" in entity["fields"], f"{entity_name} must contain id field"

    print("Model validation passed.")

if __name__ == "__main__":
    main()
