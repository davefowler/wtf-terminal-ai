"""Environment and project detection."""

import os
from pathlib import Path
from typing import Dict, List, Any


def detect_project_type(path: str = ".") -> str:
    """
    Detect project type based on config files.

    Args:
        path: Directory to check (defaults to current directory)

    Returns:
        Project type: "python", "node", "ruby", "go", "rust", or "unknown"
    """
    path_obj = Path(path)

    # Python project indicators
    python_files = [
        'requirements.txt',
        'pyproject.toml',
        'setup.py',
        'Pipfile',
        'poetry.lock',
        'environment.yml'
    ]
    if any((path_obj / f).exists() for f in python_files):
        return 'python'

    # Node.js project indicators
    if (path_obj / 'package.json').exists():
        return 'node'

    # Ruby project indicators
    ruby_files = ['Gemfile', 'Rakefile']
    if any((path_obj / f).exists() for f in ruby_files):
        return 'ruby'

    # Go project indicators
    go_files = ['go.mod', 'go.sum']
    if any((path_obj / f).exists() for f in go_files):
        return 'go'

    # Rust project indicators
    if (path_obj / 'Cargo.toml').exists():
        return 'rust'

    # Java project indicators
    java_files = ['pom.xml', 'build.gradle', 'build.gradle.kts']
    if any((path_obj / f).exists() for f in java_files):
        return 'java'

    return 'unknown'


def get_environment_context(path: str = ".") -> Dict[str, Any]:
    """
    Get environment context for the current directory.

    Args:
        path: Directory to check (defaults to current directory)

    Returns:
        Dictionary with environment information:
        - cwd: current working directory
        - project_type: detected project type
        - project_files: list of relevant config files found
    """
    path_obj = Path(path).resolve()

    # Detect project type
    project_type = detect_project_type(path)

    # Find relevant project files
    project_file_patterns = {
        'python': [
            'requirements.txt',
            'pyproject.toml',
            'setup.py',
            'setup.cfg',
            'Pipfile',
            'poetry.lock',
            'tox.ini',
            'pytest.ini',
            'environment.yml'
        ],
        'node': [
            'package.json',
            'package-lock.json',
            'yarn.lock',
            'pnpm-lock.yaml',
            'tsconfig.json',
            'webpack.config.js',
            '.npmrc'
        ],
        'ruby': [
            'Gemfile',
            'Gemfile.lock',
            'Rakefile',
            '.ruby-version'
        ],
        'go': [
            'go.mod',
            'go.sum',
            'Makefile'
        ],
        'rust': [
            'Cargo.toml',
            'Cargo.lock'
        ],
        'java': [
            'pom.xml',
            'build.gradle',
            'build.gradle.kts',
            'settings.gradle'
        ]
    }

    project_files: List[str] = []

    # Check for common files for this project type
    if project_type in project_file_patterns:
        for filename in project_file_patterns[project_type]:
            if (path_obj / filename).exists():
                project_files.append(filename)

    # Also check for other common files
    common_files = [
        '.gitignore',
        'README.md',
        'LICENSE',
        'Makefile',
        'Dockerfile',
        'docker-compose.yml',
        '.env',
        '.env.example'
    ]

    for filename in common_files:
        file_path = path_obj / filename
        if file_path.exists() and filename not in project_files:
            project_files.append(filename)

    return {
        'cwd': str(path_obj),
        'project_type': project_type,
        'project_files': sorted(project_files)
    }


def build_tool_env_context(env_context: Dict[str, Any], git_status: Any) -> Dict[str, Any]:
    """
    Build environment context dict for tool filtering.

    Args:
        env_context: Environment context from get_environment_context()
        git_status: Git status dict or None

    Returns:
        Dict with keys for tool filtering:
        - is_git_repo: bool
        - has_package_json: bool
        - has_requirements_txt: bool
        - has_cargo_toml: bool
        - has_gemfile: bool
    """
    project_files = env_context.get('project_files', [])

    return {
        'is_git_repo': git_status is not None,
        'has_package_json': 'package.json' in project_files,
        'has_requirements_txt': 'requirements.txt' in project_files or 'pyproject.toml' in project_files,
        'has_cargo_toml': 'Cargo.toml' in project_files,
        'has_gemfile': 'Gemfile' in project_files
    }
