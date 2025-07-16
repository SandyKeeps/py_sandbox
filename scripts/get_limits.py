import resource

# Function to print current resource limits
def print_resource_limits():
    # Get and print CPU time limit
    cpu_time_limit = resource.getrlimit(resource.RLIMIT_CPU)
    print(f"CPU Time Limit: Current = {cpu_time_limit[0]}, Max = {cpu_time_limit[1]}")

    # Get and print memory limit
    memory_limit = resource.getrlimit(resource.RLIMIT_AS)
    print(f"Memory Limit: Current = {memory_limit[0] / (1024 * 1024)} MB, Max = {memory_limit[1] / (1024 * 1024)} MB")

# Example usage
if __name__ == "__main__":
    print_resource_limits()
    