# Plain
A lightweight natural-english programming language (.pln)

## 1. Keywords
* **Control and logic:** `if`, `then`, `else if`, `else`, `end`
* **Articles and connectors:** `the`, `and`, `or`
* **Universal action:** `change`
* **Output:** `say;`

## 2. Grammar Rules
* **Variables and Modifications:** `change the [name]` followed by `to 100`, `by +5`, `by -5`, `to nothing`.
* **Conditions and Execution:** an action can be executed by the `if` condition, and if it succeeds, it executes a `then` block.
* **Block Closing:** `end`

## 3. Example Code
```Plain
change the humanoid to 100
if humanoid change by +5 and the humanoid is 105 then
    say; "added successfully 5 to humanoid"
else if the humanoid is 100 or the humanoid is 0 then
    say; "no changes made"
else
    say; "unexpected value"
end
```

