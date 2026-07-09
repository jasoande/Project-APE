#!/bin/bash
# Project-APE Skill Runner
# Ensures correct Python from venv is used

source ~/.project-ape-venv/bin/activate
python -m skill.orchestrator.cli "$@"
