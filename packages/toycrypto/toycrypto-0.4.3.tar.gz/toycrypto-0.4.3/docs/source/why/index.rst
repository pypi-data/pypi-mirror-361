.. include:: /../common/unsafe.rst

Motiviation
===========

This package is almost certainly not the package you are looking for.
Instead, pyca_ or SageMath_ will better suite your needs.
I created it to meet a number of my own idiosyncratic  needs.

- I don't have the flexibility of Python version that I may want when using SageMath_.

  For example, I want to have access to something that behaves a bit like SageMath's ``factor()``
  or the ability to play with elliptic curves without having do everything in Sage.
  Perhaps when `sagemath-standard <https://pypi.org/project/sagemath-standard/>`_ quickly becomes available for the latest Python versions, I won't need to have my own (failable and incomplete) pure Python substitutes for some things I need.

- I sometimes talk about these algorithms for teaching purposes. Having pure Python versions allows me to present these.

  Proper cryptographic packages, like pyca_,

  - Correctly obscure the lower level primitives I may wish to exhibit;
  - Correctly prevent use of unsafe parameters such as small keys;
  - Correctly involve a lot of abstractions in the calls to the concealed primitives.

  Those features, essential for something to be used, are not great for expository discussion.

- Some of these I created or copied for my own learning purposes.

- I have a number of "good enough" (for my purposes) implementations of things that I want to reuse.

  For example, Birthday collision calculations are things I occasionally want, and I don't want to hunt for wherever I have something like that written or rewrite it yet again.
  Likewise, I wouldn't be surprised if I'm written the extended GCD algorithm more than a dozen times
  (not all in Python), and so would like to have at least the Python version in one place

- I want to use cryptographic examples in Jupyter Notebooks.

  I also want them to be *reproducible*, which is why I am making this public.

