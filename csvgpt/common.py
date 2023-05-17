from nanoid import generate

def generateNanoIdWithPrefix(prefix = 'other'):
    generateId = generate('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 10)
    return f"{prefix}{generateId}"