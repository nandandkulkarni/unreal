"""
Dependency Resolution for Multi-Pass Execution

Resolves actor dependencies for complex choreography where actors
follow each other's paths. Uses topological sort to determine
optimal execution order.
"""

class DependencyResolver:
    """Resolves actor dependencies using topological sort
    
    Handles:
    - Cycle detection (circular dependencies)
    - Missing actor validation
    - Self-dependency prevention
    - Parallel batch optimization
    """
    
    def __init__(self, all_actors):
        """Initialize resolver
        
        Args:
            all_actors: Set of all actor names in the movie
        """
        self.all_actors = set(all_actors)
        self.graph = {}  # actor -> [depends_on_actors]
    
    def add_dependency(self, actor, depends_on):
        """Add a dependency relationship
        
        Args:
            actor: Actor that depends on another
            depends_on: Actor that must be calculated first
        
        Raises:
            ValueError: If actor depends on itself
        """
        if actor == depends_on:
            raise ValueError(f"❌ Actor '{actor}' cannot depend on itself")
        
        if actor not in self.graph:
            self.graph[actor] = []
        
        if depends_on not in self.graph[actor]:
            self.graph[actor].append(depends_on)
    
    def validate(self):
        """Validate all dependencies
        
        Raises:
            ValueError: If validation fails
        """
        # Check all referenced actors exist
        for actor, deps in self.graph.items():
            if actor not in self.all_actors:
                raise ValueError(f"❌ Actor '{actor}' has dependencies but was never defined")
            
            for dep in deps:
                if dep not in self.all_actors:
                    raise ValueError(
                        f"❌ Actor '{actor}' depends on '{dep}', but '{dep}' doesn't exist"
                    )
        
        # Detect cycles
        if self._has_cycle():
            raise ValueError("❌ Circular dependency detected in actor dependencies")
    
    def _has_cycle(self):
        """Detect circular dependencies using DFS
        
        Returns:
            True if cycle detected, False otherwise
        """
        visited = set()
        rec_stack = set()
        
        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    print(f"❌ Cycle detected: {node} → {neighbor}")
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in self.graph:
            if node not in visited:
                if dfs(node):
                    return True
        
        return False
    
    def resolve(self):
        """Resolve dependencies into execution batches using topological sort
        
        Returns:
            List of batches, where each batch is a list of actor names
            that can be executed in parallel
        
        Raises:
            ValueError: If dependencies cannot be resolved
        """
        # Validate first
        self.validate()
        
        # Calculate in-degrees (number of dependencies)
        in_degree = {actor: 0 for actor in self.all_actors}
        
        for actor, deps in self.graph.items():
            in_degree[actor] = len(deps)
        
        # Topological sort using Kahn's algorithm
        batches = []
        current_batch = sorted([a for a in self.all_actors if in_degree[a] == 0])
        
        while current_batch:
            batches.append(current_batch)
            next_batch = []
            
            # Remove current batch from graph
            for actor in current_batch:
                # Find all actors that depend on this one
                for dependent, deps in self.graph.items():
                    if actor in deps:
                        in_degree[dependent] -= 1
                        if in_degree[dependent] == 0:
                            next_batch.append(dependent)
            
            current_batch = sorted(next_batch)  # Sort for determinism
        
        # Verify all actors were processed
        processed = set(actor for batch in batches for actor in batch)
        if processed != self.all_actors:
            unprocessed = self.all_actors - processed
            raise ValueError(f"❌ Could not resolve dependencies for: {unprocessed}")
        
        return batches
