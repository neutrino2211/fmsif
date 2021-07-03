cython3 --embed engine.py
gcc -Os -I /usr/include/python3.6 -o engine engine.c -lpthread -ffreestanding -lpython3.6m -lm -lutil -ldl