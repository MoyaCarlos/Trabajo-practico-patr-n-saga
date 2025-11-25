# Orchestrator Flask application
from flask import Flask, jsonify, request
import requests
import logging

from saga_service import SagaOrquestador

MICROSERVICES = {
    'catalogo': 'http://localhost:5001',
    'compras': 'http://localhost:5002',
    'pagos': 'http://localhost:5003',
    'inventario': 'http://localhost:5004'
}