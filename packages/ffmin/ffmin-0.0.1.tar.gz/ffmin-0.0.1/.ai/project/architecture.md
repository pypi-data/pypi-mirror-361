# XMin Optimization Framework Architecture

## Overview & Philosophy

XMin is a flexible, extensible optimization framework designed to handle diverse optimization problems with multiple variable types, constraints, and objectives. The framework follows a clean separation of concerns, providing both simple functional interfaces for quick use and sophisticated object-oriented interfaces for advanced optimization scenarios.

### Core Design Principles

1. **Separation of Concerns**: Problem definition, evaluation, and optimization strategy are cleanly separated
2. **Flexible Interface**: Support for functional, simple OO, and ask-tell patterns
3. **Universal Variable Support**: Continuous, integer, categorical, binary, and mixed variable types
4. **Extensibility**: Easy to add new algorithms, problems, and evaluation strategies
5. **Performance**: Designed for both single-threaded and parallel evaluation scenarios

## Core Components

### Problem Class

The `Problem` class encapsulates the optimization problem definition, including variable bounds, types, constraints, and evaluation logic.

```python
class Problem:
    def __init__(self, 
                 bounds: List[Tuple[float, float]], 
                 variable_types: List[str] = None,
                 constraints: List[Constraint] = None,
                 **kwargs):
        """
        Define an optimization problem.
        
        Args:
            bounds: List of (min, max) tuples for each variable
            variable_types: List of variable types ('continuous', 'integer', 'categorical', 'binary')
            constraints: List of constraint objects
        """
        pass
    
    def evaluate(self, x: np.ndarray) -> Dict[str, Any]:
        """
        Evaluate a solution vector.
        
        Args:
            x: Solution vector
            
        Returns:
            Dictionary containing:
            - 'objectives': List of objective values
            - 'constraints': List of constraint violations
            - 'feasible': Boolean indicating feasibility
            - 'metadata': Additional evaluation data
        """
        pass
```

### Solution Class

The `Solution` class represents an individual solution with its variables, fitness values, and metadata.

```python
class Solution:
    def __init__(self, 
                 variables: np.ndarray,
                 objectives: List[float] = None,
                 constraints: List[float] = None,
                 feasible: bool = True,
                 metadata: Dict[str, Any] = None):
        """
        Represents a solution in the optimization process.
        
        Args:
            variables: Decision variable values
            objectives: Objective function values
            constraints: Constraint violation values
            feasible: Whether solution satisfies all constraints
            metadata: Additional solution information
        """
        pass
    
    @property
    def fitness(self) -> float:
        """Primary fitness value (first objective for single-objective problems)"""
        pass
    
    def dominates(self, other: 'Solution') -> bool:
        """Check if this solution dominates another (for multi-objective)"""
        pass
```

### Evaluator Class

The `Evaluator` class provides the bridge between `Problem` and `Solution` objects, handling the conversion of problem evaluation results into solution objects.

```python
class Evaluator:
    def __init__(self, problem: Problem):
        """
        Initialize evaluator with a problem.
        
        Args:
            problem: Problem instance to evaluate
        """
        self.problem = problem
    
    def evaluate(self, x: np.ndarray) -> Solution:
        """
        Evaluate a solution vector using the problem and return a Solution object.
        
        Args:
            x: Solution vector to evaluate
            
        Returns:
            Solution object with evaluation results
        """
        result = self.problem.evaluate(x)
        return Solution(
            variables=x,
            objectives=result['objectives'],
            constraints=result.get('constraints', []),
            feasible=result.get('feasible', True),
            metadata=result.get('metadata', {})
        )
    
    def evaluate_batch(self, X: List[np.ndarray]) -> List[Solution]:
        """Evaluate multiple solutions"""
        return [self.evaluate(x) for x in X]
```

### Algorithm Class

The `Algorithm` class serves as the base class for all optimization algorithms and provides factory methods for creating optimizer instances.

```python
class Algorithm:
    def __init__(self, **kwargs):
        """
        Initialize algorithm with parameters.
        
        Args:
            **kwargs: Algorithm-specific parameters
        """
        pass
    
    def create_optimizer(self, problem: Problem) -> 'Optimizer':
        """
        Create an optimizer instance for the given problem.
        
        Args:
            problem: Problem to optimize
            
        Returns:
            Optimizer instance implementing ask-tell interface
        """
        pass
    
    def run(self, problem: Problem, max_evaluations: int = 1000) -> 'Result':
        """
        Simple run interface for complete optimization.
        
        Args:
            problem: Problem to optimize
            max_evaluations: Maximum number of evaluations
            
        Returns:
            Result object with optimization outcome
        """
        pass
```

### Optimizer Class

The `Optimizer` class implements the ask-tell interface for interactive optimization.

```python
class Optimizer:
    def __init__(self, algorithm: Algorithm, problem: Problem):
        """
        Initialize optimizer with algorithm and problem.
        
        Args:
            algorithm: Algorithm instance
            problem: Problem to optimize
        """
        pass
    
    def ask(self, n_candidates: int = None) -> List[np.ndarray]:
        """
        Request candidate solutions for evaluation.
        
        Args:
            n_candidates: Number of candidates to generate
            
        Returns:
            List of candidate solution vectors
        """
        pass
    
    def tell(self, solutions: List[Solution]) -> None:
        """
        Provide evaluation results to the optimizer.
        
        Args:
            solutions: List of evaluated solutions
        """
        pass
    
    def get_result(self) -> 'Result':
        """Get current optimization result"""
        pass
    
    @property
    def is_converged(self) -> bool:
        """Check if optimization has converged"""
        pass
```

### Result Class

The `Result` class contains the final optimization outcome and statistics.

```python
class Result:
    def __init__(self,
                 best_solution: Solution,
                 all_solutions: List[Solution] = None,
                 n_evaluations: int = 0,
                 convergence_history: List[float] = None,
                 algorithm_info: Dict[str, Any] = None):
        """
        Optimization result container.
        
        Args:
            best_solution: Best solution found
            all_solutions: All evaluated solutions
            n_evaluations: Total number of evaluations
            convergence_history: History of best fitness values
            algorithm_info: Algorithm-specific information
        """
        pass
    
    @property
    def x(self) -> np.ndarray:
        """Best solution variables"""
        return self.best_solution.variables
    
    @property
    def fun(self) -> float:
        """Best objective value"""
        return self.best_solution.fitness
```

## Interface Patterns

### 1. Functional Interface

The simplest interface for quick optimization tasks:

```python
from xmin import minimize

# Define problem
def objective(x):
    return sum(x**2)

bounds = [(-5, 5)] * 10
problem = Problem(bounds=bounds, objective=objective)

# Optimize
result = minimize(problem, algorithm='ga', max_evaluations=1000)
print(f"Best solution: {result.x}")
print(f"Best fitness: {result.fun}")
```

### 2. Object-Oriented Simple Interface

For more control over the optimization process:

```python
from xmin import GeneticAlgorithm, Problem

# Define problem
problem = Problem(bounds=[(-5, 5)] * 10, objective=lambda x: sum(x**2))

# Create algorithm
algorithm = GeneticAlgorithm(population_size=100, mutation_rate=0.1)

# Run optimization
result = algorithm.run(problem, max_evaluations=1000)
print(f"Best solution: {result.x}")
```

### 3. Ask-Tell Interface

For maximum control and custom evaluation scenarios:

```python
from xmin import GeneticAlgorithm, Problem, Evaluator

# Define problem and evaluator
problem = Problem(bounds=[(-5, 5)] * 10, objective=lambda x: sum(x**2))
evaluator = Evaluator(problem)

# Create algorithm and optimizer
algorithm = GeneticAlgorithm(population_size=100)
optimizer = algorithm.create_optimizer(problem)

# Optimization loop
for generation in range(100):
    # Ask for candidates
    candidates = optimizer.ask()
    
    # Evaluate candidates (can be parallelized)
    solutions = evaluator.evaluate_batch(candidates)
    
    # Tell results
    optimizer.tell(solutions)
    
    # Check convergence
    if optimizer.is_converged:
        break

# Get result
result = optimizer.get_result()
print(f"Best solution: {result.x}")
```

## Variable Type System

XMin supports all common variable types through a unified interface:

### Continuous Variables
```python
problem = Problem(
    bounds=[(0, 10), (-5, 5)],
    variable_types=['continuous', 'continuous']
)
```

### Integer Variables
```python
problem = Problem(
    bounds=[(0, 10), (1, 100)],
    variable_types=['integer', 'integer']
)
```

### Categorical Variables
```python
problem = Problem(
    bounds=[(0, 3), (0, 2)],  # Number of categories
    variable_types=['categorical', 'categorical'],
    categories=[['red', 'green', 'blue', 'yellow'], ['small', 'medium', 'large']]
)
```

### Binary Variables
```python
problem = Problem(
    bounds=[(0, 1)] * 10,
    variable_types=['binary'] * 10
)
```

### Mixed Variables
```python
problem = Problem(
    bounds=[(0, 10), (0, 1), (0, 3), (-5, 5)],
    variable_types=['continuous', 'binary', 'categorical', 'integer'],
    categories=[None, None, ['A', 'B', 'C', 'D'], None]
)
```

## Constraint Handling

XMin supports various constraint types:

### Bound Constraints
Automatically handled through the bounds parameter.

### Linear Constraints
```python
from xmin import LinearConstraint

# x1 + x2 <= 5
constraint = LinearConstraint(
    coefficients=[1, 1],
    bounds=(None, 5)
)

problem = Problem(
    bounds=[(0, 10), (0, 10)],
    constraints=[constraint]
)
```

### Nonlinear Constraints
```python
from xmin import NonlinearConstraint

# x1^2 + x2^2 <= 25
def constraint_func(x):
    return x[0]**2 + x[1]**2

constraint = NonlinearConstraint(
    func=constraint_func,
    bounds=(None, 25)
)

problem = Problem(
    bounds=[(-10, 10), (-10, 10)],
    constraints=[constraint]
)
```

## Extension Points

### Custom Algorithms

```python
from xmin import Algorithm, Optimizer

class CustomAlgorithm(Algorithm):
    def create_optimizer(self, problem):
        return CustomOptimizer(self, problem)

class CustomOptimizer(Optimizer):
    def ask(self, n_candidates=None):
        # Generate candidate solutions
        pass
    
    def tell(self, solutions):
        # Update algorithm state
        pass
```

### Custom Problems

```python
from xmin import Problem

class CustomProblem(Problem):
    def evaluate(self, x):
        # Custom evaluation logic
        objectives = [self.custom_objective(x)]
        constraints = self.custom_constraints(x)
        
        return {
            'objectives': objectives,
            'constraints': constraints,
            'feasible': all(c <= 0 for c in constraints),
            'metadata': {'custom_info': 'example'}
        }
```

## Implementation Guidelines

### Performance Considerations

1. **Vectorization**: Prefer numpy operations for mathematical computations
2. **Batch Evaluation**: Support batch evaluation for parallel processing
3. **Memory Management**: Efficient storage of solutions and history
4. **Lazy Evaluation**: Avoid unnecessary computations

### Error Handling

1. **Input Validation**: Validate problem definitions and algorithm parameters
2. **Graceful Degradation**: Handle evaluation errors without crashing
3. **Informative Messages**: Provide clear error messages and suggestions

### Testing Strategy

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **Performance Tests**: Benchmark algorithm performance
4. **Regression Tests**: Ensure consistency across versions

### Documentation

1. **API Documentation**: Comprehensive docstrings for all public methods
2. **Examples**: Clear examples for common use cases
3. **Tutorials**: Step-by-step guides for different scenarios
4. **Algorithm Descriptions**: Mathematical descriptions of implemented algorithms

## Future Roadmap

### Phase 1: Core Implementation
- Basic Problem, Solution, Evaluator, and Algorithm classes
- Simple genetic algorithm implementation
- Functional and simple OO interfaces

### Phase 2: Advanced Features
- Ask-tell interface implementation
- Multi-objective optimization support
- Constraint handling mechanisms
- Additional algorithm implementations

### Phase 3: Optimization and Extensions
- Parallel evaluation support
- Advanced variable type handling
- Performance optimizations
- Visualization tools

### Phase 4: Ecosystem
- Plugin system for custom algorithms
- Integration with popular libraries
- Advanced analysis tools
- Distributed optimization support

This architecture provides a solid foundation for building a comprehensive optimization framework that can grow from simple use cases to sophisticated optimization scenarios while maintaining clean, extensible code.