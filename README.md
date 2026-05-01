# CG/CI/CD Source Repository

This repository contains project artifacts and the code generator.

## Idea

Design artifacts are the source of truth. After every change in `artifacts/model.yaml`,
Jenkins validates the artifacts, generates application code and pushes it to the generated application repository.

## Local generation

```bash
pip install -r requirements.txt
python generator/validate_model.py artifacts/model.yaml
python generator/generate.py artifacts/model.yaml ../generated-app-repo
```

## CG/CI/CD flow

```text
Project artifacts -> Code generator -> Generated app repo -> Build/Test/Docker/Deploy
```
