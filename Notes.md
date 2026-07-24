# Week1

Some general tips for prompting:

- for complex tasks, let the model be efficient, simple, clear and don't overthink or review it too much
- we can repeat the examples multiple times in system prompt to emphasize the examples
- we can repeat the output format multiple times in system prompt to emphasize the output format

## K-shot prompting

we can put more and more examples, clear, simple, effective, and add enough examples to make the model understand the task better.

Some times the exmples are not enough, we can give the model a clear and specific instruction for our task. Like very specific for our task. We can oberve the output of the model to see where is the model failing, and we can give the model specific instruction to fix the output.

We can run the model multiple times to see if the output is consistent.

After we tried tips above, we can also try to repeat all examples multiple times, just copy and paste the examples in the system prompt to emphasize the examples.

And also we can add "!" (exclamation mark) at end of the instruction to make the model understand the task better.

## tool calling prompting

- make the prompting format more structured
  - have title for each section including,
    - tell modal who he is
    - Rules for the model to follow
    - Tools he can use
    - Examples of how to use the tools
    - output format
- give the model a role
- list the rules for the model to follow
