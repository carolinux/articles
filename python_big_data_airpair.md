##Introduction

Python is a language universally praised for cutting down development time, but using it efficiently for data analysis is not without its pitfalls. The same features that make development easy in the beginning (dynamic, permissive type system) can be the downfall of large systems; and confusing libraries, slow running times and not designing with data integrity in mind can quickly eat up development time instead. This article will cover the most common time wasters encountered when working with Python and Big Data and provide suggestions to get back on track and spend time on what really matters: using creativity and scientific methods to generate insights from vast amounts of data.

##Mistake #1: Reinventing the wheel

The Python community is in a very good state when it comes to data analysis libraries that have rich functionality and have been extensively tested. So, why reinvent the wheel? 

I see this a lot during code challenges where the candidate needs to load a CSV file into memory in order to work with it. Quite a few spend a large chunk of time writing custom CSV loading functions and invariably end up with a dictionary of dictionaries which is slow to query and difficult to transform. That leaves them with little time to impress with their ability to generate insights from data.

 There truly is no reason to get bogged down with solving already solved problems - spend a few minutes to do a Google search or ask a more experienced developer for suggestions for a data analysis library.

Incidentally, one such library that's widely used at the time of this writing is [Python Pandas](http://pandas.pydata.org/). It comes with useful abstractions for dealing with large datasets, a lot of functionality for ETL (extract, transform, load) and good performance. It cuts down developer time by enabling the succinct expression of data transformations and providing functions to load, unify and store data from different sources and formats. To illustrate the former, let's say we have a CSV file with the header _Product, ItemsSold_ and we want to find the ten most popular products. Let's compare a reasonable implementation in vanilla Python and an implementation using the powerful abstractions of Python Pandas:

###Vanilla Python
<!--code lang=python linenums=true-->

    from collections import defaultdict
    header_skipped = False
    sales = defaultdict(0)
    with open(filename, 'r') as f:
        line = f.readline()
        if not header_skipped:
           header_skipped = True
           continue
        line = line.split(",")
        product = line[0]
        sales = int(line[1])
        sales[product] += sales
    top10 = sorted(sales.items(), key=lambda x:x[1], reverse=True)[:10]

###Pandas
<!--code lang=python linenums=true-->

    import pandas as pd
    data = pd.read_csv(filename)
    top10 = data.groupby("Product")["ItemsSold"].count().order(ascending=False)[:10]

Notes: Doing the task in vanilla Python does have the advantage of not needing to load the whole file in memory - however, pandas does things behind the scenes to optimize I/O and performance. Additionally, the in-memory sales dictionary of the vanilla Python solution is not lightweight either.

##Mistake #2: Not tuning for performance

When programs take too much time to produce any output, the developer's rhythm and focus are broken. Slow programs also limit the amount of experimentation a developer can do - if your program takes ten minutes to output results for a small dataset, you have the possibility to tweak and execute your program only around thirty times per day. 

So, when you find yourself sitting idly waiting for the code to execute, it may be time to try and identify bottlenecks. There are specialized utilities available to help developers profile and speedup their code. Most of these work within the [IPython interactive shell](http://www.ipython.org).

The simplest way to profile code within IPython is to use the _%timeit_ magic command to get the runtime of a Python statement. A more sophisticated tool is the _line profiler_ which you can [download](https://pypi.python.org/pypi/line_profiler/). After launching IPython, type:

    %load_ext line_profiler
    %lprun -f function_to_profile statement_that_invokes_the_fuction

Subsequently, you get an output of this form which describes what percentage of execution time was spent on which line at the function:

    Line #      Hits         Time  Per Hit   % Time  Line Contents
    ==============================================================

Using the line profiler has helped me personally identify bottlenecks with the use of the aforementioned Python Pandas library and achieve tenfold speedups by tweaking the implementation.

However, if you've reached the point where you are sure the algorithm is of optimal complexity and implementation for the problem, it may pay off to _cythonize_ parts of your code for performance. Using the _%timeit_ command from above we can compare the runtime of the uncythonized version and the cythonized one.

###Uncythonized version
Paste this into IPython:

    def sum_uncythonized():
        a = 0
        for i in range(100000):
            a += i
        return a

###Cythonized version
Install cythonmagic if you don't have it already and wiithin IPython type:

     %load_ext cythonmagic

and copy-paste the following text as a single block:

    %%cython
    def sum_cythonized():
        cdef long a = 0 # this directive defines a type for the variable
        cdef int i = 0
        for i in range(100000):
            a += i
        return a

Then view the results: 

     %timeit sum_cythonized()
    >>>10000 loops, best of 3: 52.3 µs per loop

     %timeit sum_uncythonized()
    >>>100 loops, best of 3: 3.28 ms per loop

We achieve a speed-up of two orders of magnitude just by defining types. Cythonmagic, indeed. 

##Mistake #3: Not understanding time and timezones

When programmers first work with time, Epoch time can be a strange concept to grasp. The basic concept to understand is that Epoch time is the same number around the world at any given instant but how this number is translated into hours and minutes of the day depends on the timezone and the time of the year (because of daylight savings). When working with Python, these translations are handled by the _datetime_ and _pytz_ modules.
 
Python's built-in time handling modules can be confusing both in how the functions are named and how to convert between different representations of time, much like the C time libraries it is based on internally. It is important to be able to work with it correctly, because data in timeseries format is very common. One pain point is timezone handling. A common misconception concerns the following statement:

    dt = datetime.fromtimestamp(utc_number)

When dealing with timezones for the first time, people think this returns the date and time in UTC format. In reality, it returns the date and time in the timezone of the machine the command is being ran on. This essentially makes the code non-portable. I learned this the hard way by deploying the same code in a local machine and in a machine in another country and seeing my resulting plots oddly shifted.

For timezone support, the _pytz_ module is a solution which can operate with the _datetime_ module. It can handle creation of the local time when the UTC time is known, and it also respects daylight savings rules. We can verify this by doing the following:
 <!--code lang=python linenums=true-->

    from datetime import datetime
    import pytz
    ams = pytz.timezone('Europe/Amsterdam')
    winter = datetime(2000, 11, 1, 10, 0, tzinfo=pytz.utc)
    summer = datetime(2000, 6, 1, 10, 0, tzinfo=pytz.utc)
    print summer.astimezone(ams) # CET time is +2 hours
    >>>2000-06-01 12:00:00+02:00 
    print winter.astimezone(ams) # CEST time is +1 hour
    >>>2000-11-01 11:00:00+01:00

 However, as described in the [official documentation](http://pytz.sourceforge.net/), there are several ways to use the module and get unexpected results back because interoperability with the _datetime_ module is not perfect. In the example below, we'd expect the time difference of the same date and time between UTC and the Amsterdam timezone to be one hour in winter, but, it's not:
 <!--code lang=python linenums=true-->

     td = datetime(2000, 11, 1, 10, 0, tzinfo=pytz.utc) - datetime(2000,11,1,10,0, tzinfo=ams)
     print td.total_seconds() 
    >>>1200 # 20 minutes ? (somehow pytz falls back to a long outdated timezone setting for Amsterdam)

Ultimately, Python's native time support is at times counter intuitive and at times lacking. Current solutions can be made to work, but the exposed API is confusing. Before a library of the caliber and adoption of [JodaTime](http://www.joda.org/joda-time/) in Java is implemented in Python, developers are advised to tread very carefully, test extensively that time methods do what they think they do and generally check methods whether they return time in UTC or local machine time and opt for storing and using UTC for their transformations where possible. Recent libraries that tackle the issue of providing a more intuitive API on top of the maze that is Python time handling are [Delorean](http://delorean.readthedocs.org/), [times](https://pypi.python.org/pypi/times) and [arrow](http://crsmithdev.com/arrow/). 


##Mistake #4: Manual integration with heavier technologies or other scripts

For analysing 10s of gigabytes of data, the power of a scripting languange like Python, no matter how optimized, may not be enough. It is not uncommon for developers to choose a faster framework to do the heavy lifting on the data (basic filtering and slicing) and then attack the resulting (smaller) dataset with Python to take advantage because Python is less restrictive when it comes to exploratory analysis.

 The whole process may end up looking like this: Developer launches a Java Map/Reduce job on a dataset with orders to filter on orders of products of a certain brand, waits until it's done, then uses the command line to copy the results from HDFS to the local filesystem, and then launches a Python script on the data to find the most popular products and days. This creates another result file, which in turn may be visualized by invoking a second Python script.

The problem with this approach is that manual intervention doesn't scale (in the number of tasks) and that the simple action of copying files over is a step that: 

1. gets repetitive and tiring
2. introduces more opportunity for human error (misplaced/misnamed files in this simple example or just plain forgetting to refresh files)
3. must be documented in detail if collaborators want to reproduce the developer's end results (even though copying files is a trivial action)

The solution: Automate. Treat integration of different technologies and/or different analysis steps as an issue to be solved in its own right. There are many frameworks you can use to manage a complicated data analysis pipeline, and if you like Python, you might want to check out [luigi](https://github.com/spotify/luigi) by Spotify. With luigi, you can chain together tasks of different types (Java Map/Reduce, Spark, Python, bash scripts) and create your own custom tasks. It works by letting you define a task dependency graph and the inputs, outputs and actions of each task. By invoking the luigi scheduler with the name of the last task you want to run (in our example, the visualization of the most popular products), you can sit back and relax while the necessary tasks get launched one after the other (or in parallel, where possible) to produce your end result. It is satisfying and efficient to have one-click data analysis reports generated, and it frees up your time to get more creative in analysing the data. 

##Mistake #5: Not keeping track of data types & schemata

When dealing with a variety of data sources, having the confidence that the data is valid and failing fast when it is not are two important prerequisites to maintaining the integrity of your analysis and to taking corrective measures in time. In cases like this, data integrity trumps flexibility. 

Python doesn't come with support for type validation and is in fact, designed not to. This leads into situations where the code fails quite further away from when the first error occured or unexpected values were produced. When analyzing data, we can have the situation where two different data sources that should join on a common column fail to do so because the columns have been implicitly converted to different types (str vs int) at some point in the pipeline. Or it can happen that a dataset is missing a field, but this becomes apparent several steps later, because that's when the field is accessed, making debugging more difficult and requiring a re-computation of several steps. As a result, especially when dealing with Big Data, issues like this have the potential to become major time wasters.

Python is designed to allow this, in the same way it allows for subclasses to not implement the non-implemented methods of the superclass and still be instantiated (and fail at runtime when and if these methods are accessed). That is, unless one uses the _abc_ module, first formally introduced [here](https://www.python.org/dev/peps/pep-3119), and decorates these methods as abstract. Below is an example of how the _abc_ module works:
 <!--code lang=python linenums=true-->

    from abc import ABCMeta, abstractmethod

    class MyABC:
        __metaclass__ = ABCMeta
    
        @abstractmethod
        def foo():
           pass

    bar = MyABC() # fails at instantiation, because the class has at least one method which is abstract (foo)

This concept of failing fast according to custom but succinctly defined rules is one we can borrow to mitigate the type tracking problem.

Essentially, the solution is assertive programming. At every step of the pipeline, preconditions and postconditions that the generated data must fulfill must be checked. This has the added effect of providing documentation for the code, more than a simple docstring would. A pythonic way to do this is by using decorators that check the properties of the inputs and outputs of every function that does data transformations. This is an example implementation: 

 <!--code lang=python linenums=true--> 
    def check_args(*types):
        def real_decorator(func):
            def wrapper(*args, **kwargs):
                for val, typ in zip(args, types):
                    assert isinstance(val, typ), "Value {} is not of expected type {}".format(val, typ)
                return func(*args, **kwargs)
            return wrapper
        return real_decorator

    def do_long_computation(name):
        """ dummy function """
        time.sleep(10)
        return "FruitMart"

    @check_args(str, int, int)
    def print_fruit(name, apples, oranges):
        store_name = do_long_computation(name) 
        fruit = apples + oranges
        print "{} who works at {} sold {} pieces of fruit".format(name, store_name, str(fruit))

    print_fruit("Sally", 12, 5)
    >>>Sally bought 17 pieces of fruit
    print_fruit("Sally", "1", 6)
    >>>AssertionError in decorator, so we don't need to wait for do_long_computation() to finish before failing in the addition

Notes: In this solution we do not use _kwargs_ for simplicity. For those of you who may think type checking in Python is heresy - you're still not obliged to do it everywhere and for every variable. It's up to you to determine the most pivotal points in your program where you will get value out of verifying types (for instance, before a particularly costly computation).

##Mistake #6: No data provenance tracking

An issue important to data analysis workflows is that of tracking which version of the data and algorithm was used to generate which results. If you don't do that, with an ever-changing codebase and data inputs, you end up having some result files and no clear memory of how they were generated and no good way to recreate them if there is a need, two weeks or three months from now. Additionally, it will be very hard to pinpoint or prove beyond reasonably doubt that any arising data quality problems are caused by faulty or missing input data and not by an error in the analysis. That's why it's important to keep metadata on all inputs and outputs. 

Using the _luigi_ framework as described in #5 gives you a DAG of your tasks and their inputs. That makes it possible to track all input data and code that played a part to generate a specific output, using simple graph algorithms (a simple backwards depth-first search in this case). So, make it part of the process to save this information in a text file next to the output as a courtesy to your future self. When management comes back in two weeks and asks _"Hey, Caroline, top10products_2014Nov12.csv looks wonky, are you sure we didn't sell any blue widgets on November 12?"_ you can look at **top10products_2014Nov12.csv.metadata** and see that the input file used was **SalesNov12.json** provided directly by external sources, which indeed doesn't mention any blue widgets, so it is safe to conclude that your top10 calculation is not where the issue lies.

##Mistake #7: No (regression) testing

Testing data analysis pipelines is in some ways a bit trickier than general software testing, because sometimes it's exploratory in nature so there may be no 100% fixed "right" answer. However, code that given input X gave output Y must keep doing this despite changes or the output must be changed in a way that makes it better and still acceptable given some custom but well-defined criteria.

Unit testing the functionality on a small dataset is useful but not enough - testing the application on real data of the correct size  at regular intervals and especially when major changes are made is the only way to be reasonably sure that nothing broke. When dealing with Big Data, this means that the tests would run for a long time, so what I have found works is to automate the process through a continuous integration system that runs the tests against every pull request. In conjuction with #5, that means running entire pipelines to see that the pieces also still interact as expected with each other. 

##Summary 

Working well with any tool comes down to knowing its shortcomings (and especially the ones that most affect your situation). This article has been the result of real life experience with Big Data and of continuously asking "Is there a better way of doing this?". 

When one observes that they're spending a disproportionate amount of time doing things that don't serve their end goals (for instance, loading CSV files or trying to use the _datetime_ library without understanding it), it's time to take a step back, examine your processes and discover if there is a more leveraged way of doing things. One can discover existing tools or even build upon them to solve their issues (like I've built upon the _luigi_ library to assist data provenance tracking). 

So, good luck and have fun building things! 
