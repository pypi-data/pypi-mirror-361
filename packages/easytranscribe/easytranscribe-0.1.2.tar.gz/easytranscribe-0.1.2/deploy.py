#!/usr/bin/env python3
"""
Automated deployment script for easytranscribe.

This script automates the entire deployment process:
1. Version bumping (major, minor, patch)
2. Updating version files
3. Creating git commit and tag
4. Pushing to a new branch
5. Creating a GitHub Pull Request
6. Publishing to PyPI

Usage:
    python deploy.py [major|minor|patch]

If no argument is provided, you'll be prompted to choose.
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path
from typing import Tuple, Optional


class DeploymentError(Exception):
    """Custom exception for deployment errors."""

    pass


class EasyTranscribeDeployment:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.version_file = self.project_root / "easytranscribe" / "_version.py"
        self.pyproject_file = self.project_root / "pyproject.toml"
        self.setup_file = self.project_root / "setup.py"
        self.current_version = self._get_current_version()

    def _run_command(
        self, command: str, capture_output: bool = True, check: bool = True
    ) -> subprocess.CompletedProcess:
        """Run a shell command and return the result."""
        print(f"🔧 Running: {command}")
        result = subprocess.run(
            command,
            shell=True,
            capture_output=capture_output,
            text=True,
            cwd=self.project_root,
            check=check,
        )
        if capture_output and result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return result

    def _get_current_version(self) -> str:
        """Get the current version from _version.py."""
        if not self.version_file.exists():
            raise DeploymentError(f"Version file not found: {self.version_file}")

        content = self.version_file.read_text()
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if not match:
            raise DeploymentError("Could not parse version from _version.py")

        return match.group(1)

    def _parse_version(self, version: str) -> Tuple[int, int, int]:
        """Parse version string into major, minor, patch components."""
        try:
            parts = version.split(".")
            if len(parts) != 3:
                raise ValueError("Version must have 3 parts")
            return tuple(int(part) for part in parts)
        except ValueError as e:
            raise DeploymentError(f"Invalid version format '{version}': {e}")

    def _bump_version(self, bump_type: str) -> str:
        """Bump version based on type (major, minor, patch)."""
        major, minor, patch = self._parse_version(self.current_version)

        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        elif bump_type == "patch":
            patch += 1
        else:
            raise DeploymentError(f"Invalid bump type: {bump_type}")

        return f"{major}.{minor}.{patch}"

    def _update_version_files(self, new_version: str):
        """Update version in all relevant files."""
        print(f"📝 Updating version from {self.current_version} to {new_version}")

        # Update _version.py
        version_content = f'__version__ = "{new_version}"\n'
        self.version_file.write_text(version_content)
        print(f"   ✅ Updated {self.version_file}")

        # Update pyproject.toml
        pyproject_content = self.pyproject_file.read_text()
        pyproject_content = re.sub(
            r'version\s*=\s*["\'][^"\']+["\']',
            f'version = "{new_version}"',
            pyproject_content,
        )
        self.pyproject_file.write_text(pyproject_content)
        print(f"   ✅ Updated {self.pyproject_file}")

        # Update setup.py if it has hardcoded version
        if self.setup_file.exists():
            setup_content = self.setup_file.read_text()
            if "version=" in setup_content and '"' in setup_content:
                setup_content = re.sub(
                    r'version\s*=\s*["\'][^"\']+["\']',
                    f'version="{new_version}"',
                    setup_content,
                )
                self.setup_file.write_text(setup_content)
                print(f"   ✅ Updated {self.setup_file}")

    def _check_git_status(self):
        """Check if git working directory is clean."""
        result = self._run_command("git status --porcelain")
        if result.stdout.strip():
            print("⚠️  Warning: Working directory has uncommitted changes:")
            print(result.stdout)
            response = input("Continue anyway? (y/N): ").lower()
            if response != "y":
                raise DeploymentError("Deployment cancelled due to uncommitted changes")

    def _create_git_commit_and_tag(self, new_version: str):
        """Create git commit and tag for the new version."""
        print(f"🏷️  Creating git commit and tag for version {new_version}")

        # Add changed files
        self._run_command("git add easytranscribe/_version.py pyproject.toml")
        if self.setup_file.exists():
            self._run_command("git add setup.py")

        # Create commit
        commit_message = f"Bump version to {new_version}"
        self._run_command(f'git commit -m "{commit_message}"')

        # Create tag
        tag_name = f"v{new_version}"
        self._run_command(f'git tag -a {tag_name} -m "Release {new_version}"')

        return tag_name

    def _push_to_branch(self, new_version: str):
        """Create and checkout a new branch for the release."""
        branch_name = f"release-{new_version}"
        print(f"🚀 Creating release branch: {branch_name}")

        # Create and checkout new branch
        self._run_command(f"git checkout -b {branch_name}")

        return branch_name

    def _create_github_pr(self, branch_name: str, new_version: str):
        """Create a GitHub Pull Request."""
        print(f"📋 Creating GitHub Pull Request for {branch_name}")

        # Check if gh CLI is installed
        try:
            self._run_command("gh --version")
        except subprocess.CalledProcessError:
            print("⚠️  GitHub CLI (gh) not installed. Skipping PR creation.")
            print(
                f"   Please manually create a PR from branch '{branch_name}' to 'main'"
            )
            return

        # Create PR
        title = f"Release version {new_version}"
        body = f"""
## Release {new_version}

This PR bumps the version to {new_version} and includes all changes for the new release.

### Changes:
- Version bump from {self.current_version} to {new_version}
- Updated version files (pyproject.toml, _version.py)

Ready for merge and PyPI publication.
        """.strip()

        try:
            self._run_command(
                f'gh pr create --title "{title}" --body "{body}" --base main --head {branch_name}'
            )
            print("   ✅ Pull Request created successfully!")
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  Failed to create PR: {e}")
            print(
                f"   Please manually create a PR from branch '{branch_name}' to 'main'"
            )

    def _build_package(self):
        """Build the package for PyPI."""
        print("📦 Building package for PyPI")

        # Clean previous builds
        build_dirs = ["build", "dist", "easytranscribe.egg-info"]
        for build_dir in build_dirs:
            build_path = self.project_root / build_dir
            if build_path.exists():
                self._run_command(f"rm -rf {build_dir}")

        # Install build dependencies
        self._run_command("pip install --upgrade build twine")

        # Build package
        self._run_command("python -m build")

        print("   ✅ Package built successfully!")

    def _publish_to_pypi(self, test_pypi: bool = False):
        """Publish package to PyPI."""
        target = "Test PyPI" if test_pypi else "PyPI"
        print(f"🚀 Publishing to {target}")

        # Check if API token is configured
        if test_pypi:
            repository_url = "https://test.pypi.org/legacy/"
            print("   Using Test PyPI repository")
        else:
            repository_url = "https://upload.pypi.org/legacy/"
            print("   Using production PyPI repository")

        # Upload using twine
        upload_cmd = "python -m twine upload"
        if test_pypi:
            upload_cmd += " --repository-url https://test.pypi.org/legacy/"
        upload_cmd += " dist/*"

        try:
            self._run_command(upload_cmd, capture_output=False)
            print(f"   ✅ Successfully published to {target}!")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to publish to {target}: {e}")
            print("   Please check your PyPI credentials and try again")
            return False

        return True

    def _validate_environment(self):
        """Validate that required tools are available."""
        print("🔍 Validating environment...")

        required_commands = ["git", "python", "pip"]
        for cmd in required_commands:
            try:
                self._run_command(f"{cmd} --version")
            except subprocess.CalledProcessError:
                raise DeploymentError(f"Required command '{cmd}' not found")

        # Check if we're in a git repository
        try:
            self._run_command("git rev-parse --git-dir")
        except subprocess.CalledProcessError:
            raise DeploymentError("Not in a git repository")

        print("   ✅ Environment validation passed!")

    def _finalize_deployment(self, new_version: str, branch_name: str, tag_name: str):
        """Finalize deployment by pushing to upstream and returning to develop branch."""
        print(f"🔄 Finalizing deployment...")
        
        # Get current branch (should be the release branch)
        current_branch_result = self._run_command("git branch --show-current")
        current_branch = current_branch_result.stdout.strip()
        
        print(f"   Current branch: {current_branch}")
        
        # Push all changes to upstream (origin)
        try:
            print("📤 Pushing changes to upstream...")
            
            # Push the release branch
            self._run_command(f"git push -u origin {branch_name}")
            
            # Push the tag
            self._run_command(f"git push origin {tag_name}")
            
            # Also push to upstream if it's different from origin
            try:
                upstream_result = self._run_command("git remote get-url upstream", check=False)
                if upstream_result.returncode == 0 and upstream_result.stdout.strip():
                    print("   Detected upstream remote, pushing there too...")
                    self._run_command(f"git push upstream {branch_name}")
                    self._run_command(f"git push upstream {tag_name}")
            except subprocess.CalledProcessError:
                # Upstream remote doesn't exist, which is fine
                pass
            
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  Warning: Failed to push to upstream: {e}")
            print("   You may need to push manually later")
        
        # Switch back to develop branch
        try:
            print("🔄 Switching back to develop branch...")
            
            # Check for any uncommitted changes before switching
            status_result = self._run_command("git status --porcelain")
            if status_result.stdout.strip():
                print("   ⚠️  Warning: Uncommitted changes detected, committing them first...")
                self._run_command("git add -A")
                self._run_command('git commit -m "Additional changes during deployment"')
            
            # Check if develop branch exists
            develop_exists = self._run_command("git branch --list develop", check=False)
            
            if develop_exists.returncode == 0 and "develop" in develop_exists.stdout:
                # Switch to develop branch
                self._run_command("git checkout develop")
                
                # Pull latest changes from origin/develop
                try:
                    self._run_command("git pull origin develop")
                    print("   ✅ Successfully returned to develop branch and updated")
                except subprocess.CalledProcessError:
                    print("   ✅ Returned to develop branch (no updates pulled)")
            else:
                print("   ⚠️  develop branch not found, staying on current branch")
                
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  Warning: Failed to switch to develop branch: {e}")
            print(f"   You may need to manually checkout develop: git checkout develop")

    def deploy(self, bump_type: Optional[str] = None):
        """Run the complete deployment process."""
        try:
            print("🚀 Starting EasyTranscribe deployment process...")
            print(f"   Current version: {self.current_version}")

            # Validate environment
            # self._validate_environment()

            # # Get bump type if not provided
            # if not bump_type:
            #     print("\n📋 Version bump options:")
            #     print("   1. patch  - Bug fixes (0.1.0 -> 0.1.1)")
            #     print("   2. minor  - New features (0.1.0 -> 0.2.0)")
            #     print("   3. major  - Breaking changes (0.1.0 -> 1.0.0)")

            #     while True:
            #         choice = (
            #             input("\nSelect version bump type (patch/minor/major): ")
            #             .lower()
            #             .strip()
            #         )
            #         if choice in ["patch", "minor", "major"]:
            #             bump_type = choice
            #             break
            #         print(
            #             "❌ Invalid choice. Please enter 'patch', 'minor', or 'major'"
            #         )

            # # Ensure bump_type is not None at this point
            # if not bump_type:
            #     raise DeploymentError("No bump type specified")

            # # Calculate new version
            # new_version = self._bump_version(bump_type)
            # print(
            #     f"\n📈 Version will be bumped: {self.current_version} -> {new_version}"
            # )

            # # Confirm deployment
            # confirm = input(
            #     f"\nProceed with deployment to version {new_version}? (y/N): "
            # ).lower()
            # if confirm != "y":
            #     print("❌ Deployment cancelled by user")
            #     return

            # # Check git status
            # self._check_git_status()

            # # Update version files
            # self._update_version_files(new_version)

            # # Create git commit and tag
            # tag_name = self._create_git_commit_and_tag(new_version)

            # # Push to new branch
            # branch_name = self._push_to_branch(new_version)

            # # Create GitHub PR
            # self._create_github_pr(branch_name, new_version)

            # # Ask about PyPI publication
            # print(f"\n🎯 Version {new_version} has been committed and pushed!")
            # print(f"   Branch: {branch_name}")
            # print(f"   Tag: {tag_name}")

            pypi_choice = input("\nPublish to PyPI now? (y/N): ").lower()
            if pypi_choice == "y":
                # Ask about test PyPI first
                test_choice = input(
                    "Publish to Test PyPI first? (recommended) (y/N): "
                ).lower()
                if test_choice == "y":
                    self._build_package()
                    if self._publish_to_pypi(test_pypi=True):
                        prod_choice = input(
                            "Test publication successful! Publish to production PyPI? (y/N): "
                        ).lower()
                        if prod_choice == "y":
                            self._publish_to_pypi(test_pypi=False)
                else:
                    self._build_package()
                    self._publish_to_pypi(test_pypi=False)
            else:
                print("📦 Skipping PyPI publication")
                print("   You can publish later by running:")
                print("     python -m build")
                print("     python -m twine upload dist/*")

            # Return to develop branch and push changes upstream
            # self._finalize_deployment(new_version, branch_name, tag_name)

            # print(f"\n🎉 Deployment completed successfully!")
            # print(f"   New version: {new_version}")
            # print(f"   Branch: {branch_name}")
            # print(f"   Tag: {tag_name}")
            # print(f"   Returned to develop branch")

        except KeyboardInterrupt:
            print("\n❌ Deployment cancelled by user")
            sys.exit(1)
        except DeploymentError as e:
            print(f"\n❌ Deployment failed: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Unexpected error during deployment: {e}")
            sys.exit(1)


def main():
    """Main entry point for the deployment script."""
    bump_type = None
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["-h", "--help"]:
            print("EasyTranscribe Deployment Script")
            print("=" * 40)
            print(__doc__)
            print("\nUsage:")
            print("  python deploy.py [major|minor|patch]")
            print("\nVersion bump types:")
            print("  patch  - Bug fixes (0.1.0 -> 0.1.1)")
            print("  minor  - New features (0.1.0 -> 0.2.0)")
            print("  major  - Breaking changes (0.1.0 -> 1.0.0)")
            print("\nIf no argument is provided, you'll be prompted to choose.")
            return

        bump_type = arg
        if bump_type not in ["major", "minor", "patch"]:
            print(f"❌ Invalid bump type: {bump_type}")
            print("Usage: python deploy.py [major|minor|patch]")
            print("Use --help for more information")
            sys.exit(1)

    deployment = EasyTranscribeDeployment()
    deployment.deploy(bump_type)


if __name__ == "__main__":
    main()
