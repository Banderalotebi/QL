# main.py
import sys
from src.core.graph import compile_graph

def main():
    # ... rest of the code ...

    if __name__ == '__main__':
        # ... rest of the code ...

        # Add the following line to import the record_hypothesis function
        from src.data.db import NeonLabAPI

        # ... rest of the code ...

        # Add the following line to call the record_hypothesis function
        hypothesis = "example_hypothesis"  # Define the hypothesis variable
        NeonLabAPI().record_hypothesis(hypothesis)

        # ... rest of the code ...
