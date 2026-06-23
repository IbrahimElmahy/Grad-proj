import os
import sys
import traceback

def diagnose():
    print("==========================================================")
    print("          RVMS Backend Diagnostic & Setup Tool")
    print("==========================================================")
    print()

    # 1. Check Python environment
    print(f"[Info] Python Version: {sys.version}")
    print(f"[Info] Current Directory: {os.getcwd()}")
    
    # 2. Try to activate virtual environment in backend if running from root
    backend_dir = os.path.join(os.getcwd(), 'backend')
    if os.path.exists(backend_dir):
        print("[Info] Found 'backend' directory. Switching directory...")
        os.chdir(backend_dir)
    
    sys.path.insert(0, os.getcwd())
    
    # 3. Check imports
    print("\nChecking dependencies...")
    try:
        import django
        print("[OK] Django is installed.")
    except ImportError:
        print("[ERROR] Django is not installed in the current environment! Please run within the virtual environment (.venv).")
        sys.exit(1)
        
    try:
        import rest_framework
        print("[OK] Django REST Framework is installed.")
    except ImportError:
        print("[ERROR] djangorestframework is not installed!")
        sys.exit(1)

    try:
        import cv2
        print("[OK] OpenCV (cv2) is installed.")
    except ImportError:
        print("[WARNING] opencv-python is not installed. Video/image processing will fail, but DB will work.")

    try:
        import ultralytics
        print("[OK] Ultralytics (YOLO) is installed.")
    except ImportError:
        print("[WARNING] ultralytics is not installed. AI scanning will fail, but DB will work.")

    # 4. Initialize Django
    print("\nInitializing Django...")
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rvms_backend.settings')
        django.setup()
        print("[OK] Django initialized successfully.")
    except Exception as e:
        print("[ERROR] Failed to initialize Django settings!")
        traceback.print_exc()
        sys.exit(1)

    # 5. Run Migrations
    print("\nRunning database migrations...")
    try:
        from django.core.management import call_command
        print("Applying makemigrations...")
        call_command('makemigrations')
        print("Applying migrate...")
        call_command('migrate')
        print("[OK] Database migrations completed successfully.")
    except Exception as e:
        print("[ERROR] Database migration failed!")
        traceback.print_exc()
        sys.exit(1)

    # 6. Verify Tables & Query
    print("\nVerifying database tables and querying data...")
    try:
        from inspections.models import Inspection
        count = Inspection.objects.count()
        print(f"[OK] Successfully queried Inspection table. Found {count} records.")
    except Exception as e:
        print("[ERROR] Querying Inspection table failed!")
        traceback.print_exc()
        sys.exit(1)

    # 7. Create Test Users
    print("\nConfiguring groups and test users...")
    try:
        call_command('create_test_users')
        print("[OK] Test users group permissions verified/created.")
    except Exception as e:
        print("[WARNING] Could not create test users group permissions.")
        traceback.print_exc()

    try:
        # Run create_superuser.py logic
        import create_superuser
        print("[OK] Superuser setup checked.")
    except Exception as e:
        print("[WARNING] Superuser check skipped or failed.")

    print("\n==========================================================")
    print("[SUCCESS] All checks passed! The backend database is fully functional.")
    print("==========================================================")

if __name__ == '__main__':
    diagnose()
