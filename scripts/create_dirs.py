import os

# Создаем необходимые директории
directories = [
    'app/static',
    'app/static/uploads',
    'app/static/css',
    'app/static/js'
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f"Created directory: {directory}")

print("All directories created successfully") 