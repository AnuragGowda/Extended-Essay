# A-Star
This is my implementation of the A* algorithm (visualizations were written in pygame).

The basic visualization is where the user clicks the lowest cost node until they reach the end node.

The auto visualization is an automated version of that (as the name suggests).

The other visualzation is for harder tasks, as it allows for more customization (smaller node size so that large maps can fit on your screen).

The quicksolve file takes in the raw data from the text files in the mazes folder and then puts its solution in out.txt (This is faster than the others as there is no visualization of the process).
To solve the 400x200 size maze/map it took roughly two and a half minutes on my computer.
