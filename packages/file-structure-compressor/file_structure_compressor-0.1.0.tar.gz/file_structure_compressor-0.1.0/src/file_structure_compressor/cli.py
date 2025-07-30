import argparse
from . import FileStructureCompressor

def main():
    parser = argparse.ArgumentParser(
        description="Compress a file structure into a token-efficient format."
    )
    parser.add_argument(
        "root_dir",
        help="The root directory of the project to scan.",
    )
    parser.add_argument(
        "--format",
        choices=["ascii", "json", "custom"],
        default="ascii",
        help="The output format for the file structure.",
    )
    parser.add_argument(
        "--exclude",
        help="A comma-separated list of directory and file names to exclude.",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=-1,
        help="Maximum depth to scan.",
    )

    args = parser.parse_args()

    exclude_list = args.exclude.split(',') if args.exclude else []

    compressor = FileStructureCompressor(
        root_dir=args.root_dir,
        exclude_dirs=exclude_list,
        exclude_files=exclude_list,
        depth=args.depth,
    )

    if args.format == "ascii":
        output = compressor.generate_ascii_tree()
    elif args.format == "json":
        output = compressor.generate_json_tree()
    elif args.format == "custom":
        output = compressor.generate_custom_format()
    else:
        raise ValueError(f"Unknown format: {args.format}")

    print(output)

if __name__ == "__main__":
    main()
