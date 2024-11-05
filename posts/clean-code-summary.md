# Clean Code Summary

2023-10-19

This is not a review of the book, but some notes I took while reading it. Anything not mentioned here is not a criticism of the book, but rather something I did not find interesting or useful to take notes about.

## Code as Storytelling: The Importance of Intent

One of the central ideas in Clean Code is that code should express the intent clearly.
Think of the codebase as a story - a narrative that explains how a system works to anyone reading it.

It is useful to review your own code with an "outside reader" mindset: if someone else read this, would the intent be clear? If not, there should be comments or refactoring to make it clearer. The comments should not just repeat what the code does, but rather explain why the code is written in a certain way. 

Another practical piece of advice is keeping related concepts close to each other vertically.
While modern IDEs make navigating the code easy, there's real value in structuring the code so that reading it feels natural, not like solving a puzzle.


## Objects and Data Structures

I liked the clear distinction Martin makes between objects and data structures.
- Objects hide their data behind abstractions and expose functions that operate on that data.[^1]
- Data structures expose their data and have no meaningful functions.[^1]

To dive more into the distinction, Martin defines two different approaches to calculate the areas of some shapes.

### Procedural Approach

```python
class Square:
	side: float

class Rectangle:
	height: float
	width: float

class Geometry:
    def area(shape: object) -> float:
	    if isinstance(shape, Square):
		    return shape.side ** 2
		elif isinstance(shape, Rectangle):
			return shape.height * shape.width

		return NoSuchShapeException()
```


In this approach, each shape is a simple data structure without any behavior, and the behavior (area calculation) is in the `Geometry` class.

If we need to add a `perimeter` function, we can add it to `Geometry` without touching the `Square` and `Rectangle` classes. However, every time we introduce a new shape, we have to update all functions in `Geometry`.


### Object-Oriented Approach

```python
class Square(Shape):
	side: float

	def area(self) -> float:
		return self.side ** 2 

class Rectangle(Shape):
	height: float
	width: float

	def area(self) -> float:
		return self.height * self.width  
```


In this approach, each shape encapsulates its own `area` method. This way, adding a new shape doesnt'r require any changes to existing classes, but adding new functions requires changes to each shape class.

Procedural code (code using data structures) makes it easy to add new functions without changing the existing data structures.
Object-Oriented code, makes it easy to add new classes without changing the existing functions.

These trade-offs reminded me of the classical of the [Expression Problem](https://en.wikipedia.org/wiki/Expression_problem), a classic programming dilemma that balances flexibility and extensibility.
  

## Law of Demeter

The Law of Demeter was new to me, and I found it quite useful to make sure that 
each object "knows" as less as possible about the internal details of other objects.

The [Law of Demeter](https://en.wikipedia.org/wiki/Law_of_Demeter) says "Only talk to your immediate friends"[^2]. To describe it more formally:
> Let *f* be a method of class C. *f* should only invoke the methods of:
> - C
> - *f*'s parameters
> - an object instantiated within *f*
> - an object created by *f*
  
To give a toy example, let's consider `Engine`, `Car` and `Driver` classes.

```python
class Engine:
    def get_horsepower(self) -> int:
        return 100

class Car:
    def __init__(self, engine: Engine):
        self.engine = engine

class Driver:
    def __init__(self, car: Car):
        self.car = car

    def drive(self):
        self.horsepower = self.car.engine.get_horsepower()
		print(f"Driving with {self.horsepower} horsepower")
```

Here, the `drive` method retrieves the horsepower from the `Engine` class, resulting in a chain of dependencies: `Driver` -> `Car` -> `Engine`.
The issue here is that the `Driver` knows about the internals of `Car`, and if anything changes in the `Engine` class, `Driver` might break or need modifications.

Following the Law of Demeter, the `Driver` should not know about the internals of `Car` or `Engine`.
To fix the issue, the responsibility of getting the horsepower should be given to `Car` class.

```python
class Car:
    def __init__(self, engine: Engine):
        self.engine = engine

    def get_horsepower(self) -> int:
        return self.engine.get_horsepower()

class Driver:
    def __init__(self, car: Car):
        self.car = car

    def drive(self):
        self.horsepower = self.car.get_horsepower()
		print(f"Driving with {self.horsepower} horsepower")
```

This refactor keeps `Driver` decoupled from `Engine` - the `Driver` class interacts only with the `Car` class, and does not know anything about `Engine` - , avoiding the chain of dependencies.


## Unit Tests

Not too much to add here, I just liked the F.I.R.S.T principle in chapter 9.
Which stands for:

- Fast: Tests should be fast
- Independent: Tests should not depend on each other
- Repeatable: Tests should be repeatable in any environment
- Self-Validating: The tests should have a boolean output. Either they pass or fail.
- Timely: The tests need to be written in a timely fashion. Unit tests should be written just before the production code that makes them pass.

[^1]: Martin, R. C. (2008) Clean Code: A Handbook of Agile Software Craftsmanship, Prentice Hall, Chapter 6, p. 95

[^2]: https://www2.ccs.neu.edu/research/demeter/demeter-method/LawOfDemeter/general-formulation.html

