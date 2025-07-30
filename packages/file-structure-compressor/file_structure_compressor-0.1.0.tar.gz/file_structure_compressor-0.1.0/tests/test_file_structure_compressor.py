import pytest
from pathlib import Path
from file_structure_compressor import FileStructureCompressor
import os

@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    root = tmp_path / "my_temp_project"
    root.mkdir()
    (root / "src").mkdir()
    (root / "src" / "api").mkdir()
    (root / ".git").mkdir()
    (root / "node_modules").mkdir()

    (root / "README.md").touch()
    (root / "src" / "main.py").touch()
    (root / "src" / "api" / "routes.py").touch()
    (root / ".gitignore").touch()
    return root

def test_from_directory(project_root: Path):
    compressor = FileStructureCompressor(
        root_dir=str(project_root),
        exclude_dirs=[".git", "node_modules"],
    )
    
    ascii_tree = compressor.generate_ascii_tree()
    
    expected_tree = """my_temp_project/
├── .gitignore
├── README.md
└── src/
    ├── api/
    │   └── routes.py
    └── main.py"""
    
    assert ascii_tree.replace('\r\n', '\n') == expected_tree.replace('\r\n', '\n')


def test_from_paths():
    paths = [
        os.path.join("C:", "app", "src", "main.py"),
        os.path.join("C:", "app", "src", "utils", "parser.py"),
        os.path.join("C:", "app", "config.json"),
        os.path.join("C:", "app", "README.md"),
        os.path.join("C:", "app", "src", "api", "v1", "endpoint.py"),
        os.path.join("C:", "app", "tests", "test_main.py"),
    ]
    
    compressor = FileStructureCompressor.from_paths(paths)
    ascii_tree = compressor.generate_ascii_tree()

    expected_tree = """app/
├── README.md
├── config.json
├── src/
│   ├── api/
│   │   └── v1/
│   │       └── endpoint.py
│   ├── main.py
│   └── utils/
│       └── parser.py
└── tests/
    └── test_main.py"""
    assert ascii_tree.replace('\r\n', '\n') == expected_tree.replace('\r\n', '\n')

def test_json_format(project_root: Path):
    compressor = FileStructureCompressor(str(project_root), exclude_dirs=[".git"])
    json_tree = compressor.generate_json_tree()
    
    import json
    data = json.loads(json_tree)
    
    assert "my_temp_project" in data
    assert "src" in data["my_temp_project"]
    assert "main.py" in data["my_temp_project"]["src"]

def test_custom_format(project_root: Path):
    compressor = FileStructureCompressor(str(project_root), exclude_dirs=[".git", "node_modules"])
    custom_format = compressor.generate_custom_format()
    
    expected = "my_temp_project(.gitignore,README.md,src(api(routes.py),main.py))"
    assert custom_format == expected

def test_depth_limit(project_root: Path):
    compressor = FileStructureCompressor(str(project_root), depth=1, exclude_dirs=[".git", "node_modules"])
    ascii_tree = compressor.generate_ascii_tree()
    
    expected_tree = """my_temp_project/
├── .gitignore
├── README.md
└── src/"""
    
    assert ascii_tree.replace('\r\n', '\n') == expected_tree.replace('\r\n', '\n')

def test_exclude_files(project_root: Path):
    compressor = FileStructureCompressor(
        str(project_root),
        exclude_files=["README.md"]
    )
    ascii_tree = compressor.generate_ascii_tree()
    assert "README.md" not in ascii_tree
