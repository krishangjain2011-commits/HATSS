# AGENTS.md

## HATSS – AI Agent Development Guide

Welcome to the HATSS repository.

This file defines how AI coding agents (including Codex) should work on this project.

---

# Project Overview

HATSS (House And Tech Security System) is a production-grade AI-powered cybersecurity platform designed to protect users, devices, networks, and smart homes through intelligent monitoring and AI-assisted security.

Treat this project as a real software product, not a prototype.

---

# Mission

Build secure, maintainable, scalable software that protects users while remaining simple to use.

---

# Core Principles

* Security First
* Privacy First
* Maintainability
* Scalability
* Clean Architecture
* Production-Quality Code
* Modular Design

---

# Before Writing Code

Always:

* Read the existing project structure.
* Understand the current architecture.
* Reuse existing modules where possible.
* Avoid unnecessary refactoring.
* Ask for clarification if requirements are ambiguous.

---

# Coding Standards

## Python

* Follow PEP 8.
* Use type hints.
* Keep functions small and focused.
* Use meaningful variable names.
* Write modular code.

## Frontend

* React
* TypeScript
* Functional Components
* Hooks
* Tailwind CSS
* Avoid inline styling.

## Backend

* FastAPI
* SQLAlchemy
* Alembic
* JWT Authentication

---

# Security Rules

Never:

* Store plaintext passwords.
* Hardcode secrets.
* Disable authentication.
* Trust client-side input.
* Skip validation.

Always:

* Validate inputs.
* Hash passwords.
* Use environment variables.
* Handle exceptions safely.
* Protect sensitive endpoints.

---

# AI Rules

The AI assistant must:

* Explain recommendations.
* Never invent security information.
* Never perform destructive actions automatically.
* Ask for confirmation before sensitive operations.
* Provide confidence scores when appropriate.

---

# Documentation

Every new feature should include:

* Purpose
* Architecture
* Usage
* Known limitations
* Future improvements

---

# Testing

Every feature should include:

* Unit tests
* Integration tests (where appropriate)
* Manual verification steps

Do not consider a feature complete until it has been tested.

---

# Dependencies

Before adding a new dependency:

* Prefer the Python standard library where practical.
* Use actively maintained packages.
* Avoid unnecessary dependencies.

---

# Performance

* Write clean code before optimizing.
* Measure performance before making optimizations.
* Avoid premature optimization.

---

# Code Quality Checklist

Before completing a task:

* Code builds successfully.
* Tests pass.
* Formatting passes.
* Linting passes.
* Documentation is updated.
* No duplicated logic.
* No debug code remains.

---

# Workflow

Implement only the requested feature.

Do not build unrelated functionality.

Keep changes focused and easy to review.

---

# Long-Term Vision

Every design decision should support the future HATSS ecosystem:

* Desktop Application
* Mobile Application
* Cloud Platform
* AI Security Copilot
* Smart Home Integration
* Enterprise Dashboard

---

# Final Instruction

Think like a senior software engineer.

Prioritize maintainability, security, and clarity over clever solutions.

Leave the repository in a better state than you found it.
