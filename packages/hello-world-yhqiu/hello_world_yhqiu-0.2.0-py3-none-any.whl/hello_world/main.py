"""
Main module for hello world functionality
"""

def hello():
    """Print a simple hello world message"""
    print("Hello, World!")
    return "Hello, World!"

def greet(name="World"):
    """
    Greet someone by name
    
    Args:
        name (str): Name to greet, defaults to "World"
        
    Returns:
        str: Greeting message
    """
    message = f"Hello, {name}!"
    print(message)
    return message

def main():
    """Main entry point for command line usage"""
    hello()

if __name__ == "__main__":
    main()
