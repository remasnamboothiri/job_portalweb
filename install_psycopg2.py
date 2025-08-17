import subprocess
import sys

def install_psycopg2():
    """Install psycopg2-binary for the current Python version"""
    try:
        # Try to install psycopg2-binary
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
        print("✅ psycopg2-binary installed successfully!")
        return True
    except subprocess.CalledProcessError:
        try:
            # Try alternative installation method
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "psycopg2-binary"])
            print("✅ psycopg2-binary installed successfully (user install)!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install psycopg2-binary")
            return False
    except FileNotFoundError:
        print("❌ pip not found. Please install pip first.")
        return False

if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    print("Installing psycopg2-binary...")
    
    if install_psycopg2():
        print("\n🎉 Installation complete! You can now use PostgreSQL with Django.")
        print("\nNext steps:")
        print("1. Run: python manage.py migrate")
        print("2. Your PostgreSQL database is ready!")
    else:
        print("\n⚠️  Manual installation required:")
        print("1. Download psycopg2-binary wheel from: https://pypi.org/project/psycopg2-binary/#files")
        print("2. Choose the wheel for your Python version and Windows")
        print("3. Install with: pip install downloaded_wheel_file.whl")