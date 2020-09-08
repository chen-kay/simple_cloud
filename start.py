import os

def init_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_ky.settings')
    import django
    django.setup()

if __name__ == '__main__':
    init_django()
    from cloud.fs.thread import fs_thread
    from time import sleep
    fs_thread.start_status_thead()
    while True:
        sleep(1)
