# InventoryOps

InventoryOps is a simple inventory tracking web application built as an academic DevOps course project. The application is intentionally small, while the project demonstrates a complete CI/CD flow using GitHub, Jenkins, Docker, Ansible, Azure, Prometheus, and Grafana.

## Features

- Add, edit, delete, and list inventory items
- Track item category, quantity, location, status, and notes
- Highlight low-stock items using configurable thresholds
- Filter by status and low-stock state
- Search inventory from the browser
- Export inventory data as CSV
- Health endpoint for deployment checks
- Prometheus metrics for HTTP traffic and inventory operations

## Tech Stack

- Backend: FastAPI, Python 3.11, pytest
- Frontend: plain HTML, CSS, and JavaScript
- Storage: local JSON file mounted through Docker volume
- Containers: Docker and Docker Compose
- CI/CD: GitHub and Jenkins
- Deployment: Ansible on Azure VM
- Registry: Azure Container Registry
- Monitoring: Prometheus and Grafana
- Infrastructure: minimal Terraform for Azure VM, network security group, and Azure Container Registry

## Architecture

```text
GitHub -> Jenkins -> pytest -> Docker build -> Azure ACR -> Ansible deploy -> Azure VM container
                                                              |
                                                              v
                                                   Prometheus + Grafana
```

The app runs as one FastAPI container. FastAPI serves both the REST API and the static frontend. Inventory data is saved in `data/inventory.json`, which is mounted as a Docker volume so data survives container replacement.

## API

- `GET /health`
- `GET /metrics`
- `GET /api/items`
- `POST /api/items`
- `GET /api/items/{item_id}`
- `PUT /api/items/{item_id}`
- `DELETE /api/items/{item_id}`
- `GET /api/items/export`

## Local Setup

Python must be run through a virtual environment.

```bash
python -m venv venv
source ./venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

On Windows:

```powershell
python -m venv venv
./venv/Scripts/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

Open the app at:

```text
http://127.0.0.1:8000
```

## Run Tests

```bash
source ./venv/bin/activate
pytest backend/tests
```

On Windows:

```powershell
./venv/Scripts/activate
pytest backend/tests
```

## Run With Docker Compose

Create `.env` from `.env.example`, then run:

```bash
docker compose -f docker/docker-compose.yml up --build
```

Services:

- App: `http://localhost:8000`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

Grafana default login is `admin` / `admin`.

## CI/CD Overview

The Jenkins pipeline:

1. Checks out the GitHub repository
2. Creates and uses a Python virtual environment
3. Installs backend dependencies
4. Runs pytest
5. Builds a Docker image
6. Pushes the image to Azure Container Registry
7. Runs Ansible to deploy the latest image on the Azure VM
8. Verifies `/health`

## Monitoring

Prometheus scrapes the FastAPI `/metrics` endpoint. The app exposes:

- Default HTTP request metrics
- `inventory_operations_total`
- `inventory_operation_duration_seconds`
- `inventory_items_total`
- `inventory_low_stock_total`

Grafana is preconfigured with Prometheus as a datasource.

## Project Note

This project is designed for a final semester Computer Engineering DevOps course. It avoids unnecessary production complexity such as Kubernetes, microservices, databases, authentication, or background queues so the CI/CD and monitoring workflow remains clear.
