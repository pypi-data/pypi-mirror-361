Usage
=====

Command line:

.. code-block:: bash

   prlgen -f input.csv -t 0 -c 1 -k 1 -n output -o 1

Arguments:

Library usage:

.. code-block:: python

   from prlgen import create_random_list
   output_list, min_k = create_random_list(input_list, cond_col, trial_col, k)
   # output_list is the randomized list
   # min_k is the minimal feasible repetition value used

Integration Example: PsychoPy
-----------------------------
See `examples/example_1.py` for a ready-to-use integration with PsychoPy.
