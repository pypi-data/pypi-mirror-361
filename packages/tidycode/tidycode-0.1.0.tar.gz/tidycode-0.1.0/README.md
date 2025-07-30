# 🧼 tidycode

✨ Un utilitaire CLI pour rendre vos projets Python propres, organisés et conformes aux bonnes pratiques DevSecOps.

---
[![PyPI - Version](https://img.shields.io/pypi/v/tidycode.svg)](https://pypi.org/project/tidycode/)
[![Python Versions](https://img.shields.io/pypi/pyversions/tidycode.svg)](https://pypi.org/project/tidycode/)
[![License](https://img.shields.io/pypi/l/tidycode.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/mawuva/tidycode/actions/workflows/test.yml/badge.svg)](https://github.com/mawuva/tidycode/actions/workflows/test.yml)

---

## 🚀 Fonctionnalités principales

- Initialisation rapide des fichiers de configuration (`pyproject.toml`, `.pre-commit-config.yaml`, etc.)
- Intégration de linters et formatters : `black`, `ruff`, `isort`, `mypy`
- Support de `pre-commit`, `commitizen`, `safety`, `bandit`, etc.
- CLI basée sur `Typer` : simple, claire, typée
- Séparation des commandes : qualité, sécurité, hooks, dépendances

---

## 🛠️ Installation

```bash
pip install tidycode
```

ou

```bash
poetry add tidycode

poetry add -D tidycode
```

---

## 📦 Utilisation de base

```bash
tidycode init
```

Configure automatiquement :
 - Black
 - Ruff
 - isort
 - mypy
 - Commitizen
 - pre-commit

## ✅ Qualité de code

```bash
tidycode quality setup-all
```

Ajoute tous les outils dans pyproject.toml (black, ruff, etc.)

## 🤖 Pré-commit

```bash
tidycode hooks install
```

Installe .pre-commit-config.yaml et les hooks associés.

## 🔐 Sécurité

```bash
tidycode security scan
```
Analyse des vulnérabilités avec safety et bandit.


## 🧪 Tests

```bash
pytest
```

```bash
pytest --cov=src
```

ou simplement

```bash
tidycode cov
```

## 📓 Convention de commits

```bash
tidycode commitizen bump
```
Gère automatiquement le versioning et les changelogs via Commitizen.

## 📄 Licence

Ce projet est sous licence MIT.
