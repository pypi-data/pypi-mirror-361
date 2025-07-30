import os
from pathlib import Path
import json
from typing import List, Dict, Optional, Any

class FileStructureCompressor:
    def __init__(
        self,
        root_dir: str,
        exclude_dirs: Optional[List[str]] = None,
        exclude_files: Optional[List[str]] = None,
        depth: int = -1,
        _build_fs: bool = True,
    ):
        self.root_dir = Path(root_dir).resolve()
        self.exclude_dirs = set(exclude_dirs) if exclude_dirs else set()
        self.exclude_files = set(exclude_files) if exclude_files else set()
        self.depth = depth
        if _build_fs:
            self.tree = self._build_tree_from_fs()
        else:
            self.tree = {}

    @classmethod
    def from_paths(
        cls,
        paths: List[str],
        depth: int = -1,
    ):
        if not paths:
            raise ValueError("Input path list cannot be empty.")

        if os.name == 'nt':
            normalized_paths = [p.replace('\\', '/') for p in paths]
            common_path_str = os.path.commonpath(normalized_paths)
        else:
            common_path_str = os.path.commonpath(paths)
        
        common_root = Path(common_path_str)

        instance = cls(str(common_root), depth=depth, _build_fs=False)
        instance.tree = instance._build_tree_from_paths(paths, common_root)
        return instance

    def _build_tree_from_fs(self) -> Dict[str, Any]:
        tree = {}
        root_name = self.root_dir.name
        tree[root_name] = self._scan_dir(self.root_dir, 0)
        return tree

    def _scan_dir(self, path: Path, current_depth: int) -> Dict[str, Any]:
        if self.depth != -1 and current_depth >= self.depth:
            return {}

        tree: Dict[str, Any] = {}
        try:
            for item in sorted(path.iterdir()):
                if item.name in self.exclude_dirs or item.name in self.exclude_files:
                    continue

                if item.is_dir():
                    tree[item.name] = self._scan_dir(item, current_depth + 1)
                else:
                    tree[item.name] = None
        except PermissionError:
            pass
        return tree

    def _build_tree_from_paths(self, paths: List[str], common_root: Path) -> Dict[str, Any]:
        tree = {}
        root_name = common_root.name
        tree[root_name] = {}

        for path_str in paths:
            path = Path(path_str)
            relative_path = path.relative_to(common_root)
            parts = list(relative_path.parts)
            
            if self.depth != -1 and len(parts) > self.depth:
                continue

            current_level = tree[root_name]
            for part in parts[:-1]:
                current_level = current_level.setdefault(part, {})
            
            if parts:
                current_level[parts[-1]] = None
        
        return tree

    def generate_ascii_tree(self) -> str:
        if not self.tree:
            return ""
        
        root_name = list(self.tree.keys())[0]
        lines = [f"{root_name}/"]
        self._build_ascii_lines(lines, self.tree[root_name], "")
        return "\n".join(lines)

    def _build_ascii_lines(self, lines: List[str], tree: Dict[str, Any], prefix: str):
        entries = sorted(tree.keys())
        for i, entry in enumerate(entries):
            connector = "├── " if i < len(entries) - 1 else "└── "
            is_dir = isinstance(tree[entry], dict)
            
            entry_text = f"{entry}/" if is_dir else entry
            lines.append(f"{prefix}{connector}{entry_text}")
            
            if is_dir:
                extension = "│   " if i < len(entries) - 1 else "    "
                self._build_ascii_lines(lines, tree[entry], prefix + extension)

    def generate_json_tree(self) -> str:
        return json.dumps(self.tree, indent=4)

    def generate_custom_format(self) -> str:
        if not self.tree:
            return ""
        
        root_name = list(self.tree.keys())[0]
        content = self._build_custom_format_string(self.tree[root_name])
        return f"{root_name}({content})"

    def _build_custom_format_string(self, tree: Dict[str, Any]) -> str:
        entries = []
        for name, content in sorted(tree.items()):
            if content is None:
                entries.append(name)
            else:
                entries.append(f"{name}({self._build_custom_format_string(content)})")
        return ",".join(entries)
