import subprocess
import sys


def run_command(command):
    """Run a shell command and return the output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(result.returncode)
    return result.stdout.strip()


def delete_tag(tag):
    """Delete a Git tag locally and remotely."""
    print(f"Deleting local tag '{tag}'...")
    run_command(f"git tag -d {tag}")

    print(f"Deleting remote tag '{tag}'...")
    run_command(f"git push origin :refs/tags/{tag}")


def create_and_push_tag(tag, branch):
    """Create a Git tag at the head of a branch and push it to remote."""
    print(f"Creating tag '{tag}' at the head of branch '{branch}'...")
    run_command(f"git tag {tag} {branch}")

    print(f"Pushing tag '{tag}' to remote...")
    run_command(f"git push origin {tag}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python move-tag.py <version>")
        sys.exit(1)

    version = sys.argv[1]
    tag = f"v{version}"
    branch = f"release-{version}"

    delete_tag(tag)
    create_and_push_tag(tag, branch)
    print(
        f"Tag '{tag}' has been moved to the head of branch '{branch}' and pushed to remote."
    )


if __name__ == "__main__":
    main()
