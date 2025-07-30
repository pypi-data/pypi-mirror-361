import sys
from .project_setup import create_project

def main():
    if len(sys.argv) != 2:
        print("Usage: brickdjango <project_name>")
        sys.exit(1)
    project_name = sys.argv[1]
    create_project(project_name)

if __name__ == "__main__":
    main()
