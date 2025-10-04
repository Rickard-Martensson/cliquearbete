from typing import List, Tuple, Set, FrozenSet
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Global configuration
SHOW_FULL_LIST = False  # Set to True to see all configurations, False for just breakdown
SHOW_SIZE_LABELS = True  # Set to True to show "1:", "2:", etc., False for just numbers
COUNT_UP_TO = 12


class CliqueConfiguration:
    """Represents a configuration of cliques over numbers 1..n"""
    
    def __init__(self, cliques: List[Set[int]]):
        """
        cliques: list of sets, where each set is a clique
        Each number should appear in 1 or 2 cliques
        """
        self.cliques = [set(c) for c in cliques]
    
    def __hash__(self):
        # Convert to frozensets for hashing
        return hash(frozenset(frozenset(c) for c in self.cliques))
    
    def __eq__(self, other):
        if not isinstance(other, CliqueConfiguration):
            return False
        return set(frozenset(c) for c in self.cliques) == set(frozenset(c) for c in other.cliques)
    
    def get_number_count(self) -> dict:
        """Returns how many cliques each number appears in"""
        count = {}
        for clique in self.cliques:
            for num in clique:
                count[num] = count.get(num, 0) + 1
        return count
    
    def is_valid(self) -> bool:
        """Check if each number appears in 1 or 2 cliques"""
        counts = self.get_number_count()
        return all(1 <= c <= 2 for c in counts.values())
    
    def remove_subsets(self) -> 'CliqueConfiguration':
        """Remove cliques that are proper subsets of other cliques"""
        filtered = []
        for i, clique1 in enumerate(self.cliques):
            is_subset = False
            for j, clique2 in enumerate(self.cliques):
                if i != j and clique1 < clique2:  # proper subset
                    is_subset = True
                    break
            if not is_subset:
                filtered.append(clique1)
        return CliqueConfiguration(filtered)
    
    def visualize(self) -> str:
        """Visualize the configuration with colored brackets"""
        if not self.cliques:
            return ""
        
        # Get max number
        max_num = max(max(c) for c in self.cliques)
        
        # For each number, track which cliques it belongs to
        num_to_cliques = {i: [] for i in range(1, max_num + 1)}
        for idx, clique in enumerate(self.cliques):
            for num in clique:
                num_to_cliques[num].append(idx)
        
        # Build visualization string
        result = []
        
        # Color cycling for brackets
        colors = [Fore.GREEN, Fore.BLUE, Fore.CYAN, Fore.MAGENTA, Fore.YELLOW, Fore.RED, Fore.WHITE, Fore.LIGHTBLACK_EX]
        
        # Track open brackets for each clique
        open_cliques = {}
        
        for pos in range(1, max_num + 1):
            clique_indices = num_to_cliques[pos]
            
            # Determine which cliques start at this position
            starting = []
            for c_idx in clique_indices:
                clique = self.cliques[c_idx]
                if min(clique) == pos:
                    starting.append(c_idx)
                    open_cliques[c_idx] = min(clique)
            
            # Add opening brackets
            for c_idx in starting:
                color = colors[c_idx % len(colors)]
                if len(clique_indices) == 2:
                    result.append(color + "(")
                else:
                    result.append(color + "[")
            
            # Add the number
            result.append(str(pos))
            
            # Determine which cliques end at this position
            ending = []
            for c_idx in clique_indices:
                clique = self.cliques[c_idx]
                if max(clique) == pos:
                    ending.append(c_idx)
            
            # Add closing brackets
            for c_idx in ending:
                color = colors[c_idx % len(colors)]
                if len(num_to_cliques[pos]) == 2 or (c_idx in open_cliques and 
                    any(num_to_cliques[n] and len(num_to_cliques[n]) == 2 
                        for clq in self.cliques if c_idx == self.cliques.index(clq) for n in clq)):
                    # Use parentheses for overlapping cliques
                    has_overlap = any(len(num_to_cliques[n]) == 2 for n in self.cliques[c_idx])
                    if has_overlap:
                        result.append(color + ")")
                    else:
                        result.append(color + "]")
                else:
                    result.append(color + "]")
            
            result.append(" ")
        
        return "".join(result).strip() + Style.RESET_ALL


def generate_cliques(n: int) -> List[CliqueConfiguration]:
    """Generate all valid clique configurations for numbers 1..n"""
    
    if n == 1:
        return [CliqueConfiguration([{1}])]
    
    if n == 2:
        return [
            CliqueConfiguration([{1}, {2}]),  # [1] [2]
            CliqueConfiguration([{1, 2}])      # [1 2]
        ]
    
    # Get configurations for n-1
    prev_configs = generate_cliques(n - 1)
    new_configs = []
    
    for config in prev_configs:
        # a. Add a bracket of size 1 to the end
        new_conf = CliqueConfiguration(config.cliques + [{n}])
        new_configs.append(new_conf)
        
        # b-d. Add brackets containing element i and n for each i from n-1 down to 1
        for i in range(n - 1, 0, -1):
            # Create a new clique containing i and all numbers from i to n
            new_clique = set(range(i, n + 1))
            new_conf = CliqueConfiguration(config.cliques + [new_clique])
            new_configs.append(new_conf)
    
    # Remove subsets
    new_configs = [conf.remove_subsets() for conf in new_configs]
    
    # Remove duplicates
    unique_configs = list(set(new_configs))
    
    # Filter to only valid configurations
    valid_configs = [conf for conf in unique_configs if conf.is_valid()]
    
    return valid_configs


def get_ending_clique_size(config: CliqueConfiguration, n: int) -> int:
    """Get the size of the clique containing n (the last element)"""
    for clique in config.cliques:
        if n in clique:
            return len(clique)
    return 0


def main():
    print("Clique Configuration Generator")
    print("=" * 50)
    print()
    
    # First pass: generate all configs and find maximum count for padding
    all_configs = {}
    all_size_counts = {}
    global_max_count = 0
    
    for n in range(1, COUNT_UP_TO):
        configs = generate_cliques(n)
        all_configs[n] = configs
        
        # Count configurations by ending clique size
        size_counts = {}
        for config in configs:
            size = get_ending_clique_size(config, n)
            size_counts[size] = size_counts.get(size, 0) + 1
        all_size_counts[n] = size_counts
        
        # Track global maximum for padding
        if size_counts:
            global_max_count = max(global_max_count, max(size_counts.values()))
    
    count_width = len(str(global_max_count))
    
    # Second pass: display with consistent padding
    for n in range(1, COUNT_UP_TO):
        configs = all_configs[n]
        size_counts = all_size_counts[n]
        
        # Display breakdown by ending clique size with consistent padding
        breakdown = []
        for size in range(1, n + 1):
            count = size_counts.get(size, 0)
            if count > 0:
                if SHOW_SIZE_LABELS:
                    # Make the index red and pad the count
                    breakdown.append(f"{Fore.RED}{size}{Style.RESET_ALL}: {count:>{count_width}}")
                else:
                    # Just show the count
                    breakdown.append(f"{count:>{count_width}}")
        
        if SHOW_SIZE_LABELS:
            print(f"n = {n}: {len(configs)} configurations")
            print(f"  Ending clique breakdown: {', '.join(breakdown)}")
        else:
            print(f"n = {n}: {len(configs)} configurations = {', '.join(breakdown)}")
        
        if SHOW_FULL_LIST:
            print("-" * 50)
            for i, config in enumerate(configs, 1):
                size = get_ending_clique_size(config, n)
                print(f"{i:2d}. {config.visualize()}  (ending size: {size})")
        
        print()
    
    # Verify the recurrence relation: a_{n+1} = 3*a_n - 1
    print("Verifying recurrence relation: a_{n+1} = 3*a_n - 1")
    print("=" * 50)
    
    counts = []
    for n in range(1, COUNT_UP_TO):
        configs = all_configs[n]
        count = len(configs)
        counts.append(count)
        
        size_counts = all_size_counts[n]
        
        # Display breakdown by ending clique size with consistent padding
        breakdown = []
        for size in range(1, n + 1):
            cnt = size_counts.get(size, 0)
            if cnt > 0:
                breakdown.append(f"{cnt:>{count_width}}")
            else:
                breakdown.append(f"{'0':>{count_width}}")
        breakdown_str = " + ".join(breakdown)
        
        if n == 1:
            print(f"a_1 = {count} = [{breakdown_str}]")
        else:
            expected = 3 * counts[-2] - 1
            match = "✓" if count == expected else "✗"
            print(f"a_{n} = {count} = [{breakdown_str}], expected 3*{counts[-2]} - 1 = {expected} {match}")


if __name__ == "__main__":
    main()
