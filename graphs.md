***Representations of graphs***
-> Graphs can be represented in two ways:
    1. Collection of adjacency lists
    2. Adjacency matrix

A size of the graph is represented by two parameters:
  - V -> # of vertices (nodes)
  - E -> # of edges (connections)

*!!*
-> Adjacency-list *(AL)* representation provides a compact way to represent *sparse* graphs:
  - Those for which |E| << |V|^2
  - i.e. graphs with not many connections
-> Adjacency-matrix *(AM)* representation is preferred when the graph is *dense*
  - |E| ~= |V|^2
  - Or when we need to be able to quickly tell if there is an edge connecting two given Vs

**AL Representation**
for a graph G = (V, E)
Adj = List[|V| Lists (one for each vertex)]

for each u in V, Adj[u] contains all vertices v such that there is an edge (u, v) in E 

If G is a *directed* graph, the sum of lengths of all the adjacency lists is |E|
If G is an *undirected* graph, the sum of lengths of all the adjacency lists is 2|E|

**AL representation of weighted graphs**
Let G = (V, E) be weighted graph with weight function w s.t. w: E -> R
  - We simply store the weight w(u, v) of the edge (u, v) in E with vertex v in u's AL

**AM Representation**
for a graph G = (V, E),
assume that the vertices are numbered 1, 2,...,|V| in some arbitrary manner
=> The AM representation of graph G consists of a |V|*|V| matrix A = (a_(i,j)) s.t.
    - a_(i,j) = 1 if (i, j) in E
    - a_(i,j) = 0 if (i, j) not in E

If G is an *undirected* graph A = A^T
If G is a *directed* graph, the above property does not hold.

*!!*
In some applications it can be smart to store only the upper half of the matrix (diag included)

**AM representation of weighted graphs**
for a graph G = (V, E),
assume that the vertices are numbered 1, 2,...,|V| in some arbitrary manner
=> The AM representation of graph G consists of a |V|*|V| matrix A = (a_(i,j)) s.t.
    - a_(i,j) = w if (i, j) in E
    - a_(i,j) = nil || 0 || inf if (i, j) not in E
-> The nil value chosen for a non-edge can vary depending on application and use case

***Search***

**BFS on graphs**
given a graph G = (V, E) and a distinguished source vertex *s*,
BFS systematically explores the edges of G to "discover" every vertex that is reachable from s
  - it computes the distance (smallest # of edges) from *s* to each reachable vertex
  - it also produces a "breadth-first tree" with root *s* that contains all reachable vertices
  - for any vertex v reachable from *s*, the simple path in the BF tree from *s* -> *v*
    corresponds to a "shortest path" from *s* -> *v* in G (path containing smallest # edges)
  - Works on both directed and undirected graphs

-> To keep track of progress, BFS colors each vertex white, gray or black
  - All vertices start out white and may later become gray/black
  - A vertex is *discovered* the first time it is encountered during search -> becomes non-white
    - Gray and black vertices == discovered, BFS still distinguishes between them to ensure that search
      proceeds in a breadth-first manner
    - if (u, v) in E and vertex u is black => vertex v is either gray or black
      - i.e. all vertices adjacent to black vertices have been discovered
        - *black vertices* are vertices for which all adjacent vertices have been *discovered*
    - Gray vertices may have some adjacent white vertices;
      - they represent the frontier between discovered and undiscovered vertices
      - gray set may contain:
        1. remaining vertices at breadth-level k
        2. newly discovered vertices at breadth-level k+1

-> BFS constructs a BF-tree:
  1. Initially contains only its root (source vertex *s*)
  2. Whenever the search discovers a white vertex *v* in the course of scanning AL of an already
     discovered vertex *u*, the vertex *v* and the edge *(u,v)* are added to the tree
      - For a given edge *(u,v)* We say that *u* is the *predecessor* or *parent* of *v* in the BF-tree 

-> *Shortest paths*
  - Define the *shortest-path distance d(s, v)* from s -> v as the min # of edges in any path from s -> v
    - If there is no path from s -> v, d(s,v) = +inf
    - We call a path of length d(s,v) **a shortest path** from s to v
      - There might be multiple paths of length d(s,v)

**!!**
*Theorem: Correctness of BFS*
  - Let G = (V, E) be a directed or undirected graph, and suppose that BFS is run on G from a given
    source vertex s in V. Then, during its execution, BFS discovers every vertex v in V that is
    reachable from source s, and upon termination, v.d = d(s,v) for all v in V. Moreover, for any
    vertex v != s that is reachable from s, one of the shortest paths from s to v is a shortest path
    from s to v.pi followed by the edge (v.pi, v), *w/ v.pi = predecessor of v*

**DFS on graphs**
DFS explores edges out of the most recently discovered vertex *v* that still has unexplored edges leaving it.
Once all of *v's* edges have been explored, the search "backtracks" to explore edges leaving the vertex
from which v was discovered.
This process continues until we have discovered all the vertices that are reachable from the original source. 

  - As in BFS whenever DFS discovers a vertex *v* during a scan of the AL of an already discovered *u*,
    it records this event by setting *v's* predecessor attribute v.pi to u
  - Unlike BFS, whose predecessor subgraph forms a tree, the predecessor subgraph produced by DFS may
    be composed of several trees, because the search may repeat from multiple sources

**DF forest**
  - The predecessor subgraph of a DFS forms a *depth-first forest* comprising of several df-trees
  - As in BFS, DFS colors vertices during the search to indicate state.
    1. Each vertex is initially white
    2. Vertices are grayed when discovered in the search
    3. Vertices are blackened when it is finished, i.e. the AL has been examined completely for the vertex
  - *This guarantees that each vertex ends up with exactly one depth-first tree, so these are disjoint*
  - Besides creating a DF forest, DFS also *timestamps* each vertex.
    - Each vertex v has two timestamps:
      1. v.d -> records when v is first discovered (and grayed)
      2. v.f -> records when the search finishes examining v's adjacency list (and blackens v)
    - These timestamps provide important info about the structure of the graph and are generally helpful
      in reasining about the behavior of DFS

*Theorem: Paranthesis theorem*
In any DFS of a directed or undirected graph G = (V, e), for any two vertices u, v exactly one of the
following holds:
  - intervals [u.d, u.f] and [v.d, v.f] are entirely disjoint, and neither u nor v is a descendant of the
    other in the DF forest
  - interval [u.d, u.f] is contained entirely within the interval [v.d, v.f], and u is a descendant of
    v in a DF tree
  - interval [v.d, v.f] is contained entirely within the interval [u.d, u.f], and v is a descendant of
    u in a DF tree

*Theorem: White-path theorem*
In a DF forest of a directed or undirected graph G = (V, E), vertex v is a descendant of vertex u IFF at
the time that the search discovers u, there is a path from u to v consisting entirely of white vertices

*Classification of edges*
We can define four edge types in terms of the DF forest G_pi produced by a DFS on G:
  1. *Tree edges* -> edges in the DF forest G_pi. Edge (u, v) is a tree edge if v was first discovered
     by exploring edge (u, v), i.e. edge used to *FIRST* discover a vertex
  2. *Back edges* -> edges (u, v) connecting a vertex u to an ancestor v in a DF tree. We consider
     self-loops, which may occur in directed graphs, to be back edges
  3. *Forward edges* -> non-tree edges (u, v) connecting a vertex u to a descentant v in a DF tree, i.e.
     u -> v but v was already discovered (is gray)
  4. *Cross edges* -> all other edges. They can go between vertices in the same DF tree, as long as one
     vertex is not an ancestor of the other, or they can go between vertices in different DF trees. i.e.
     the intervals [u.d, u.f] & [v.d, v.f] are *disjoint*

*Theorem: Edge classification for undirected graphs*
In a DFS of an undirected graph G, every edge of G is either a tree edge or back edge

***Topological Sort***
A topo sort of a DAG G = (V, E) is a linear ordering of all its vertices s.t. if G contains an edge (u, v),
then u appears before v in the ordering.
  - If the graph contains a cycle (aka non-acyclic), then no ordering is possible
  - We can view a topo sort of a graph as an ordering of its vertices along a horizontal line so that all
    directed edges go from left to right
-> Many applications use DAG to indicate precedences among events.

*We can apply topo sort both via DFS and BFS, specific application goes beyond the motive of these notes*

*Strongly-connected components*
In a directed graph, a strongly-connected component (SCC) is:
  - A maximal set of vertices where every vertex can reach every other vertex via directed paths
    - Maximal means that you cannot add another vertex without breaking this property

***Spanning tree***
Suppose you have a *connected undirected graph*, a spanning tree is:
  - A graph is connected if:
    - For every pair of vertices u, v -> there exists a path between them
  - A subset of edges that connects all vertices without creating cycles 
    - It "spans" all vertices.
    - It is a tree (connected + acyclic)
    - A spanning tree being a tree in our specific case guarantees that entry and exit
      will be connected by one path and one path only
    -> In a connected acyclic graph (a tree applies), there is exactly one simple path
       between any two vertices
      - Proof by contradiction:
        - suppose there were two different paths between A and B.
        - combining them forms a cycle
        - but trees have no cycle (or a connected acyclic graph has no cycle)
        -> Contradiction

**! Key property**
If a graph has n vertices:
  - Any spanning tree has exactly n-1 edges

***Minimum spanning trees***
Since all spanning trees have exactly the same "edge" cost of n-1 w/ n the # of vertices of the graph:
  - A minimum spanning tree is the spanning tree whose total edge weight is the smallest.
    - Obviously this can be identified only on weighted graphs


=> Wilson's algorithm to generate spanning trees (perfect mazes)

```pseudo
function wilson(grid):

    for each cell in grid:
        in_tree[cell] = false

    # Choose an arbitrary root
    root = random_cell(grid)
    in_tree[root] = true

    # While there are cells not yet in the tree
    while exists cell s.t. in_tree[cell] == false:

        start = random cell where in_tree[start] == false

        path = loop_erased_random_walk(start, in_tree)

        # Add path to the tree
        for i from 0 to path.length - 2:
            a = path[i]
            b = path[i+1]

            remove_wall(a, b)
            in_tree[a] = true

        in_tree[path.last] = true


function loop_erased_random_walk(start, in_tree):
    current = start
    parth = empty list
    visited_index = empty map # cell -> index in path

    while in_tree[current] == false:
        if current in visited_index:
            # LOOP DETECTED
            loop_start_index = visited_index[current]

            # erase everything after that index
            path = path[0 : loop_start_index + 1]

            # rebuild visited_index accordingly
            rebuild visited_index from path
        else:
            visited_index[current] = path.length
            append current to path
        # step randomly
        next = random choice among neighbors(current)
        current = next

    # when we hit tree, append final cell
    append current to path

    return path
```


