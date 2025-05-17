import torch

print(f"\nPyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA version detected by PyTorch: {torch.version.cuda}")
    print(f"cuDNN version detected by PyTorch: {torch.backends.cudnn.version()}")
    print(f"Device count: {torch.cuda.device_count()}")
    for i in range(torch.cuda.device_count()):
        print(f"Device {i} name: {torch.cuda.get_device_name(i)}")
else:
    print("CUDA not detected by PyTorch.")

# Teste simples de alocação de tensor na GPU
try:
    if torch.cuda.is_available():
        tensor = torch.tensor([1.0, 2.0]).cuda()
        print("\nSuccessfully allocated tensor to CUDA device.")
        print(tensor)
    else:
        print("\nCannot allocate tensor to CUDA device as CUDA is not available.")
except Exception as e:
    print(f"\nError during CUDA tensor allocation test: {e}")
