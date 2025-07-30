import os
import subprocess
import sys

from django_custom_structure.docker_data import DOCKER_CONTENT
from django_custom_structure.git_data import GIT_IGNORE_CONTENT
from django_custom_structure.setting_data import DEVELOPMENT_SETTING_BLOCK, PRODUCTION_SETTING_BLOCK
from django_custom_structure.base_data import BASE_SETTING


def create_project(project_name):
    base_path = os.path.join(os.getcwd(), project_name)
    os.makedirs(base_path, exist_ok=True)
    print(f"""
          --------------------------------------------------------------------------- ---------------------------------------------------------------------------
                                                                Created project directory {base_path}.
          --------------------------------------------------------------------------- ---------------------------------------------------------------------------
        """)

    # Create virtual environment
    venv_path = os.path.join(base_path, 'venv')
    subprocess.run([sys.executable, '-m', 'venv', venv_path], check=True)
    print("""
          --------------------------------------------------------------------------- ---------------------------------------------------------------------------
                                                                        Virtual environment created.
          --------------------------------------------------------------------------- ---------------------------------------------------------------------------
        """)

    # Determine OS-specific paths and executable names
    if sys.platform == 'win32':
        venv_bin_dir = 'Scripts'
        pip_executable = 'pip.exe'
        django_admin_executable = 'django-admin.exe'
    else:
        venv_bin_dir = 'bin'
        pip_executable = 'pip'
        django_admin_executable = 'django-admin'

    pip_path = os.path.join(venv_path, venv_bin_dir, pip_executable)
    django_admin_path = os.path.join(venv_path, venv_bin_dir, django_admin_executable)

    # Print activation instructions
    if sys.platform == 'win32':
        print(f"""
          --------------------------------------------------------------------------- ---------------------------------------------------------------------------
                                                             To activate venv (CMD): {venv_path}\\Scripts\\activate.bat
                                                             To activate venv (PowerShell): {venv_path}\\Scripts\\Activate.ps1
          --------------------------------------------------------------------------- ---------------------------------------------------------------------------
            """)
    else:
        print(f"""
          --------------------------------------------------------------------------- ---------------------------------------------------------------------------
                                                             To activate venv: source {venv_path}/bin/activate
          --------------------------------------------------------------------------- ---------------------------------------------------------------------------
            """)

    # Install Django
    subprocess.run([pip_path, 'install', 'django'], check=True)
    print("""
          --------------------------------------------------------------------------- ---------------------------------------------------------------------------
                                                                            Django installed.
          --------------------------------------------------------------------------- ---------------------------------------------------------------------------
        """)

    # Install django-environ
    subprocess.run([pip_path, 'install', 'django-environ'], check=True)
    print("""
          --------------------------------------------------------------------------- ---------------------------------------------------------------------------
                                                                            Django-Environ installed.
          --------------------------------------------------------------------------- ---------------------------------------------------------------------------
        """)

    # Start Django project
    subprocess.run([
        django_admin_path,
        'startproject', 'config', base_path
    ], check=True)
    print("""
          --------------------------------------------------------------------------- ---------------------------------------------------------------------------
                                                                            Django project created.
          --------------------------------------------------------------------------- ---------------------------------------------------------------------------
        """)

    # Create folder structure
    os.makedirs(os.path.join(base_path, 'config', 'settings'), exist_ok=True)
    os.makedirs(os.path.join(base_path, 'apps'), exist_ok=True)
    os.makedirs(os.path.join(base_path, 'base'), exist_ok=True)

    # Move settings.py to settings/base.py and replace contents with BASE_SETTING
    old_settings = os.path.join(base_path, 'config', 'settings.py')
    new_base_settings = os.path.join(base_path, 'config', 'settings', 'base.py')

    with open(new_base_settings, 'w') as f:
        f.write(BASE_SETTING)
    print(f"New base.py file created at: {new_base_settings}")

    # Create dev and prod settings files
    dev_settings = os.path.join(base_path, 'config', 'settings', 'development.py')
    prod_settings = os.path.join(base_path, 'config', 'settings', 'production.py')

    # Init settings package and apps package
    open(os.path.join(base_path, 'config', 'settings', '__init__.py'), 'a').close()
    open(os.path.join(base_path, 'apps', '__init__.py'), 'a').close()
    open(os.path.join(base_path, 'base', '__init__.py'), 'a').close()

    print("""
          --------------------------------------------------------------------------- ---------------------------------------------------------------------------
                                                                    __init__.py created in apps/ folder.
          --------------------------------------------------------------------------- ---------------------------------------------------------------------------
        """)

    # Create .env file in settings/ folder
    env_path = os.path.join(base_path, 'config', 'settings', '.env')
    open(env_path, 'a').close()
    print("""
          --------------------------------------------------------------------------- ---------------------------------------------------------------------------
                                                                    .env file created in config/settings/ folder.
          --------------------------------------------------------------------------- ---------------------------------------------------------------------------
        """)

    # Extract SECRET_KEY from old settings and add to .env
    sec_key = None
    if os.path.exists(old_settings):
        with open(old_settings, 'r') as f:
            lines = f.readlines()
        for line in lines:
            if 'SECRET_KEY' in line:
                sec_key = line.strip()
                break

        if sec_key:
            print('Found SECRET_KEY:', sec_key)
            sec_key_clean = "".join(sec_key.split())
            with open(env_path, 'a') as f:
                f.write(f'{sec_key_clean}\n')
            print('SECRET_KEY added to .env file.')
        else:
            print('No SECRET_KEY found.')

    # Write dev and prod settings files with imported blocks
    with open(prod_settings, 'w') as f:
        f.write('\n' + PRODUCTION_SETTING_BLOCK + '\n')

    with open(dev_settings, 'w') as f:
        f.write('\n' + DEVELOPMENT_SETTING_BLOCK + '\n')

    print("""
            --------------------------------------------------------------------------- ---------------------------------------------------------------------------
                                                                Moved DEBUG and DATABASES settings to development.py and production.py.
                                                                    Base settings imported into development and production files.
            --------------------------------------------------------------------------- ---------------------------------------------------------------------------
        """)

    manage_py_path = os.path.join(base_path, 'manage.py')

    # Update manage.py to set DJANGO_SETTINGS_MODULE to development by default
    if os.path.exists(manage_py_path):
        with open(manage_py_path, 'r') as f:
            content = f.read()

        new_content = content.replace(
            "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')",
            "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')"
        )

        # Remove old settings.py
        if os.path.exists(old_settings):
            os.remove(old_settings)

        with open(manage_py_path, 'w') as f:
            f.write(new_content)

        print("""
                --------------------------------------------------------------------------- ---------------------------------------------------------------------------
                                                    Updated manage.py to use config.settings.development as default settings.
                --------------------------------------------------------------------------- ---------------------------------------------------------------------------
            """)

    # Write .gitignore
    with open(os.path.join(base_path, '.gitignore'), 'w') as f:
        f.write(GIT_IGNORE_CONTENT.strip())
    print("""
            --------------------------------------------------------------------------- ---------------------------------------------------------------------------
                                                                            .gitignore file created.
            --------------------------------------------------------------------------- ---------------------------------------------------------------------------
        """)

    # Write Dockerfile
    dockerfile_path = os.path.join(base_path, "Dockerfile")
    with open(dockerfile_path, 'w') as f:
        f.write(DOCKER_CONTENT.strip())
    print("""
            --------------------------------------------------------------------------- ---------------------------------------------------------------------------
                                                                                Dockerfile created.
            --------------------------------------------------------------------------- ---------------------------------------------------------------------------
        """)

    # Create requirements.txt using pip freeze from the venv
    with open(os.path.join(base_path, 'requirements.txt'), 'w') as req_file:
        subprocess.run([pip_path, 'freeze'], stdout=req_file, check=True)
    print("""
            --------------------------------------------------------------------------- ---------------------------------------------------------------------------
                                                                            requirements.txt created.
            --------------------------------------------------------------------------- ---------------------------------------------------------------------------
        """)
