"""
CI/CD Pipeline Tests
Tests for GitHub Actions workflows, Docker configurations, and deployment scripts
"""

import os
import subprocess
import yaml
import pytest
from pathlib import Path


# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class TestGitHubActionsWorkflows:
    """Tests for GitHub Actions CI/CD workflows"""
    
    def test_ci_workflow_exists(self):
        """Test that CI workflow file exists"""
        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
        assert workflow_path.exists(), "CI workflow file should exist"
    
    def test_cd_workflow_exists(self):
        """Test that CD workflow file exists"""
        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "cd.yml"
        assert workflow_path.exists(), "CD workflow file should exist"
    
    def test_ci_workflow_valid_yaml(self):
        """Test that CI workflow is valid YAML"""
        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
        with open(workflow_path, 'r') as f:
            data = yaml.safe_load(f)
        assert data is not None, "CI workflow should parse as valid YAML"
        assert 'name' in data, "CI workflow should have a name"
        # YAML converts 'on' to boolean True, check both
        assert 'on' in data or True in data, "CI workflow should have triggers"
        assert 'jobs' in data, "CI workflow should have jobs"
    
    def test_cd_workflow_valid_yaml(self):
        """Test that CD workflow is valid YAML"""
        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "cd.yml"
        with open(workflow_path, 'r') as f:
            data = yaml.safe_load(f)
        assert data is not None, "CD workflow should parse as valid YAML"
        assert 'name' in data, "CD workflow should have a name"
        # YAML converts 'on' to boolean True, check both
        assert 'on' in data or True in data, "CD workflow should have triggers"
        assert 'jobs' in data, "CD workflow should have jobs"
    
    def test_ci_workflow_has_required_jobs(self):
        """Test that CI workflow has all required jobs"""
        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
        with open(workflow_path, 'r') as f:
            data = yaml.safe_load(f)
        
        jobs = data.get('jobs', {})
        assert 'lint' in jobs, "CI workflow should have a lint job"
        assert 'test' in jobs, "CI workflow should have a test job"
        assert 'security-scan' in jobs, "CI workflow should have a security-scan job"
        assert 'build-check' in jobs, "CI workflow should have a build-check job"
    
    def test_cd_workflow_has_required_jobs(self):
        """Test that CD workflow has all required jobs"""
        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "cd.yml"
        with open(workflow_path, 'r') as f:
            data = yaml.safe_load(f)
        
        jobs = data.get('jobs', {})
        assert 'build-and-push' in jobs, "CD workflow should have a build-and-push job"
        assert 'deploy-staging' in jobs, "CD workflow should have a deploy-staging job"
        assert 'deploy-production' in jobs, "CD workflow should have a deploy-production job"
    
    def test_ci_workflow_uses_correct_python_versions(self):
        """Test that CI workflow tests multiple Python versions"""
        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
        with open(workflow_path, 'r') as f:
            data = yaml.safe_load(f)
        
        test_job = data.get('jobs', {}).get('test', {})
        strategy = test_job.get('strategy', {})
        matrix = strategy.get('matrix', {})
        python_versions = matrix.get('python-version', [])
        
        assert '3.11' in python_versions, "CI should test Python 3.11"
        assert len(python_versions) >= 2, "CI should test multiple Python versions"


class TestDockerConfiguration:
    """Tests for Docker configuration files"""
    
    def test_dockerfile_exists(self):
        """Test that Dockerfile exists"""
        dockerfile_path = PROJECT_ROOT / "Dockerfile"
        assert dockerfile_path.exists(), "Dockerfile should exist"
    
    def test_dockerfile_has_valid_syntax(self):
        """Test that Dockerfile has valid content"""
        dockerfile_path = PROJECT_ROOT / "Dockerfile"
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        assert 'FROM' in content, "Dockerfile should have FROM instruction"
        assert 'WORKDIR' in content, "Dockerfile should have WORKDIR instruction"
        assert 'COPY' in content, "Dockerfile should have COPY instruction"
        assert 'RUN' in content, "Dockerfile should have RUN instruction"
        assert 'EXPOSE' in content, "Dockerfile should have EXPOSE instruction"
        assert 'CMD' in content, "Dockerfile should have CMD instruction"
    
    def test_dockerfile_uses_multi_stage_build(self):
        """Test that Dockerfile uses multi-stage build"""
        dockerfile_path = PROJECT_ROOT / "Dockerfile"
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        assert content.count('FROM') >= 2, "Dockerfile should use multi-stage build"
    
    def test_dockerfile_has_python(self):
        """Test that Dockerfile uses Python"""
        dockerfile_path = PROJECT_ROOT / "Dockerfile"
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        assert 'python' in content.lower(), "Dockerfile should use Python"
    
    def test_dockerfile_exposes_correct_ports(self):
        """Test that Dockerfile exposes correct ports"""
        dockerfile_path = PROJECT_ROOT / "Dockerfile"
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        assert '8000' in content, "Dockerfile should expose port 8000 (API)"
        assert '8501' in content, "Dockerfile should expose port 8501 (Dashboard)"
    
    def test_docker_compose_exists(self):
        """Test that docker-compose.yml exists"""
        compose_path = PROJECT_ROOT / "docker-compose.yml"
        assert compose_path.exists(), "docker-compose.yml should exist"
    
    def test_docker_compose_valid_yaml(self):
        """Test that docker-compose.yml is valid YAML"""
        compose_path = PROJECT_ROOT / "docker-compose.yml"
        with open(compose_path, 'r') as f:
            data = yaml.safe_load(f)
        
        assert data is not None, "docker-compose.yml should parse as valid YAML"
        assert 'services' in data, "docker-compose.yml should have services"
    
    def test_docker_compose_has_required_services(self):
        """Test that docker-compose has all required services"""
        compose_path = PROJECT_ROOT / "docker-compose.yml"
        with open(compose_path, 'r') as f:
            data = yaml.safe_load(f)
        
        services = data.get('services', {})
        assert 'app' in services, "docker-compose should have app service"
        assert 'neo4j' in services, "docker-compose should have neo4j service"
    
    def test_dockerignore_exists(self):
        """Test that .dockerignore exists"""
        dockerignore_path = PROJECT_ROOT / ".dockerignore"
        assert dockerignore_path.exists(), ".dockerignore should exist"
    
    def test_dockerignore_has_required_entries(self):
        """Test that .dockerignore has important entries"""
        dockerignore_path = PROJECT_ROOT / ".dockerignore"
        with open(dockerignore_path, 'r') as f:
            content = f.read()
        
        assert '.git' in content, ".dockerignore should ignore .git"
        assert '__pycache__' in content, ".dockerignore should ignore __pycache__"
        # *.py[cod] covers .pyc files
        assert '*.py[cod]' in content, ".dockerignore should ignore .pyc files"


class TestCI_CDScripts:
    """Tests for CI/CD helper scripts"""
    
    def test_run_tests_script_exists(self):
        """Test that run_tests.sh exists"""
        script_path = PROJECT_ROOT / "scripts" / "run_tests.sh"
        assert script_path.exists(), "run_tests.sh should exist"
    
    def test_run_tests_script_is_executable(self):
        """Test that run_tests.sh is executable"""
        script_path = PROJECT_ROOT / "scripts" / "run_tests.sh"
        assert os.access(script_path, os.X_OK), "run_tests.sh should be executable"
    
    def test_lint_code_script_exists(self):
        """Test that lint_code.sh exists"""
        script_path = PROJECT_ROOT / "scripts" / "lint_code.sh"
        assert script_path.exists(), "lint_code.sh should exist"
    
    def test_lint_code_script_is_executable(self):
        """Test that lint_code.sh is executable"""
        script_path = PROJECT_ROOT / "scripts" / "lint_code.sh"
        assert os.access(script_path, os.X_OK), "lint_code.sh should be executable"
    
    def test_run_tests_script_has_correct_shebang(self):
        """Test that run_tests.sh has correct shebang"""
        script_path = PROJECT_ROOT / "scripts" / "run_tests.sh"
        with open(script_path, 'r') as f:
            first_line = f.readline().strip()
        
        assert first_line == '#!/bin/bash', "run_tests.sh should use bash"
    
    def test_lint_code_script_has_correct_shebang(self):
        """Test that lint_code.sh has correct shebang"""
        script_path = PROJECT_ROOT / "scripts" / "lint_code.sh"
        with open(script_path, 'r') as f:
            first_line = f.readline().strip()
        
        assert first_line == '#!/bin/bash', "lint_code.sh should use bash"


class TestDependabotConfiguration:
    """Tests for Dependabot configuration"""
    
    def test_dependabot_config_exists(self):
        """Test that dependabot.yml exists"""
        config_path = PROJECT_ROOT / ".github" / "dependabot.yml"
        assert config_path.exists(), "dependabot.yml should exist"
    
    def test_dependabot_config_valid_yaml(self):
        """Test that dependabot.yml is valid YAML"""
        config_path = PROJECT_ROOT / ".github" / "dependabot.yml"
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        
        assert data is not None, "dependabot.yml should parse as valid YAML"
        assert 'updates' in data, "dependabot.yml should have updates"
    
    def test_dependabot_has_pip_updates(self):
        """Test that dependabot is configured for pip"""
        config_path = PROJECT_ROOT / ".github" / "dependabot.yml"
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        
        updates = data.get('updates', [])
        pip_update = next((u for u in updates if u.get('package-ecosystem') == 'pip'), None)
        assert pip_update is not None, "dependabot should have pip updates configured"
    
    def test_dependabot_has_github_actions_updates(self):
        """Test that dependabot is configured for GitHub Actions"""
        config_path = PROJECT_ROOT / ".github" / "dependabot.yml"
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        
        updates = data.get('updates', [])
        actions_update = next((u for u in updates if u.get('package-ecosystem') == 'github-actions'), None)
        assert actions_update is not None, "dependabot should have GitHub Actions updates configured"


class TestRequirementsFile:
    """Tests for requirements.txt"""
    
    def test_requirements_file_exists(self):
        """Test that requirements.txt exists"""
        req_path = PROJECT_ROOT / "requirements.txt"
        assert req_path.exists(), "requirements.txt should exist"
    
    def test_requirements_has_testing_deps(self):
        """Test that requirements.txt has testing dependencies"""
        req_path = PROJECT_ROOT / "requirements.txt"
        with open(req_path, 'r') as f:
            content = f.read()
        
        assert 'pytest' in content, "requirements.txt should include pytest"
        assert 'pytest-cov' in content, "requirements.txt should include pytest-cov"
    
    def test_requirements_has_linting_deps(self):
        """Test that requirements.txt has linting dependencies"""
        req_path = PROJECT_ROOT / "requirements.txt"
        with open(req_path, 'r') as f:
            content = f.read()
        
        assert 'flake8' in content, "requirements.txt should include flake8"
        assert 'black' in content, "requirements.txt should include black"
        assert 'mypy' in content, "requirements.txt should include mypy"
    
    def test_requirements_has_security_deps(self):
        """Test that requirements.txt has security dependencies"""
        req_path = PROJECT_ROOT / "requirements.txt"
        with open(req_path, 'r') as f:
            content = f.read()
        
        assert 'bandit' in content, "requirements.txt should include bandit"
        assert 'safety' in content, "requirements.txt should include safety"


class TestPytestConfiguration:
    """Tests for pytest configuration"""
    
    def test_pytest_ini_exists(self):
        """Test that pytest.ini exists"""
        pytest_path = PROJECT_ROOT / "pytest.ini"
        assert pytest_path.exists(), "pytest.ini should exist"
    
    def test_pytest_ini_valid(self):
        """Test that pytest.ini is valid"""
        pytest_path = PROJECT_ROOT / "pytest.ini"
        with open(pytest_path, 'r') as f:
            content = f.read()
        
        assert '[pytest]' in content, "pytest.ini should have [pytest] section"
        assert 'testpaths' in content, "pytest.ini should define testpaths"


class TestCIWorkflowTriggers:
    """Tests for CI/CD workflow triggers"""
    
    def test_ci_triggers_on_push(self):
        """Test that CI workflow triggers on push"""
        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
        with open(workflow_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # YAML converts 'on' to True
        triggers = data.get('on', data.get(True, {}))
        push = triggers.get('push', {})
        branches = push.get('branches', [])
        
        assert 'main' in branches, "CI should trigger on push to main"
        assert 'develop' in branches, "CI should trigger on push to develop"
    
    def test_ci_triggers_on_pull_request(self):
        """Test that CI workflow triggers on pull request"""
        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
        with open(workflow_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # YAML converts 'on' to True
        triggers = data.get('on', data.get(True, {}))
        pr = triggers.get('pull_request', {})
        
        assert pr is not None, "CI should trigger on pull requests"
    
    def test_cd_triggers_on_tags(self):
        """Test that CD workflow triggers on version tags"""
        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "cd.yml"
        with open(workflow_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # YAML converts 'on' to True
        triggers = data.get('on', data.get(True, {}))
        push = triggers.get('push', {})
        tags = push.get('tags', [])
        
        assert any('v*' in str(tag) for tag in tags), "CD should trigger on version tags"
    
    def test_cd_has_workflow_dispatch(self):
        """Test that CD workflow can be manually triggered"""
        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "cd.yml"
        with open(workflow_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # YAML converts 'on' to True
        triggers = data.get('on', data.get(True, {}))
        assert 'workflow_dispatch' in triggers, "CD should support manual trigger"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

