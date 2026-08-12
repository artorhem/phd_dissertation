# FlexoGraph Dissertation Outline

**Purpose**: Subsection-level outline for deciding final dissertation structure.
**Legend**:
- **[MAIN]** — Content exists on the current main branch (SIGMOD submission)
- **[CANDIDACY]** — Content exists only on the candidacy branch (more verbose, older)
- **[BOTH]** — Content exists on both branches
- **[TO WRITE]** — Content that would need to be written or substantially expanded
- **[DECIDE]** — TBD
---
## Preliminary Pages
- Title page
- Committee page
- Abstract **[MAIN]**
- Lay summary **[CANDIDACY]** — needs updating for final submission
- Preface **[CANDIDACY]** — needs updating
- Table of contents
- List of tables
- List of figures
- Glossary **[BOTH]** — acronyms: RDBMS, OLTP, OLAP, HTAP, HGTAP, CSR, CRUD, API, WT, GAPBS
- Acknowledgements **[TO WRITE]** — currently a TODO placeholder
---
## Chapter 1: Introduction [Estimate: 1 day]
### Graphs Are Ubiquitous **[MAIN]**

- Large graphs in social networks, Web, recommendation, fraud detection, biology
- Graphs with billions of nodes, trillions of edges
- Graph elements carry labels (types) and properties (key-value attributes)
- Distinction between graph structure (topology) and graph semantics (properties/labels)

### Graph Workloads: OLTP vs. OLAP **[MAIN]**
- Graph OLTP: interactive, latency-sensitive queries (e.g., find user's latest posts, real-time fraud detection at 20ms)
- Graph OLAP: whole-graph analysis (e.g., PageRank, community detection)
- Central issue: two workload classes served by different systems
- Dual-silo approach creates ETL overhead and consistency challenges

### Current Approaches and Their Limitations **[MAIN]**
- **Databases as primary store**: Facebook TAO (MySQL + offline pipelines), Oracle PGX (in-memory graph server), SQL/PGQL extensions (transient in-memory representations)
- Relational traversals reduce to recursive self-joins with costs growing with path length
- **Specialized graph databases** (Neo4j, ArangoDB): handle OLTP well, perform poorly on OLAP
- **Graph processing systems** (Pregel, GraphX, Ligra, GraphChi): strong OLAP, lack OLTP; require costly ETL
- The central dichotomy: graph databases provide persistent storage but underperform on OLAP; analytics systems need costly preprocessing

### Hybrid Systems (HGTAP) **[MAIN]**
- LiveGraph: mmap-backed adjacency lists, serializes writers, limited insertion throughput
- GART: in-memory multi-versioned CSR, bounded by main-memory capacity
- Neither handles the full spectrum of real operating conditions

### Key Observations **[MAIN]**
1.  Data layout is the key performance determinant and layout construction time is non-trivial (time building layout, not running algorithm)
	1. <span style="color:rgb(192, 0, 0)">This is probably where we should advocate for single-node optimization before scale-out.</span>
	2. <span style="color:rgb(192, 0, 0)">Mention parallelizable data structures, efficient algorithms, generic but expressive APIs.</span>
2. Transaction management is expensive to build from scratch (ACID, crash recovery, concurrency control)
3. No single operating regime suffices (in-memory, out-of-core, distributed each have limitations)
	1. <span style="color:rgb(192, 0, 0)">This is where we can also discuss the COST metric and the “communication cost” discussed in Scott Beamers thesis. This is in the candidacy doc</span>
4. Most existing systems target a single operating point; few perform across the entire spectrum
  
### FlexoGraph: Our Approach **[MAIN]**
- Design philosophy: build on WiredTiger KV store rather than building custom storage engine <span style="color:rgb(192, 0, 0)">and is a best-of-both worlds design point</span>
- Inherits: transaction manager, write-ahead log, buffer pool
- Two analytics-friendly structural layouts encoded as sorted key ranges (adjacency lists, CSR approximation)
- Typed property storage layer supporting embedded and columnar modes
- Insertion throughput scales near-linearly to 72 threads (1.48M edges/sec)
- Library API exposing read-only snapshot iterators for neighborhoods/properties
- Spider chart result: FlexoGraph delivers robust performance across entire operating spectrum

### Contributions **[MAIN]**
1. FlexoGraph design: hybrid graph database on WT unifying OLTP/OLAP without ETL/preprocessing
2. Analysis of analytics-friendly layouts: adjacency-list and CSR-like representations encoded as sorted key ranges in KV store to preserve scan locality
3. Typed property storage: embedded and columnar modes with property-mutation latencies 3–4 orders of magnitude lower than Neo4j/JanusGraph/ArangoDB
4. Efficient read-only neighborhood iterators on snapshots with flexible partitioning strategy
5. Evaluation showing: matches analytics performance of in-memory/out-of-core systems, scales insertion throughput near-linearly, delivers transactional performance of in-memory dynamic graph containers

<span style="color:rgb(192, 0, 0)">> <b>[DECIDE]</b>: Should the bulk loader be listed as a contribution?</span>

### Dissertation Organization **[TO WRITE]**
- Chapter-by-chapter roadmap

---

## Chapter 2: Background [Estimate: 1 day]

- preamble to introduce the chapter
### 2.1 Graph Models **[BOTH]**
#### 2.1.1 Structural Graphs
- G = (V, E), directed/undirected, weighted graphs G = (V, E, w)
- Captures topology and connectivity for analytics (shortest paths, centrality, community detection)

#### 2.1.2 Property Graph Model
- Extends structural graph: vertices and edges carry labels (types) and properties (key-value attributes)
- Labels analogous to relational tables; properties analogous to columns
- Vertices with same label share common attribute schema
- Structural graph derived from property graph by selecting elements with specific labels and discarding properties

#### 2.1.3 Access Patterns on Graph Data **[TO WRITE / expand from BOTH]**
- Point queries: retrieve a single vertex's properties by ID
- Aggregate queries: count edges of a given type
- Multi-hop traversals with property access: friends-of-friends with property filters
- BI scans: scan all vertices of a label, filter by a property
- Write operations: insert vertex with properties, update property values
- Why property access patterns differ fundamentally from structural access patterns

### 2.2 Graph Workloads **[BOTH]**

#### 2.2.1 Graph OLTP
- Queries accessing small subset of graph; latency-sensitive, short-running, transactional
- Examples: find node's neighborhood, insert/update vertices or edges
#### 2.2.2 Graph OLAP
- Long-running, complex, analyzing large portions or entire graph
- Examples: BFS, PageRank, community detection, shortest path, pattern mining

#### 2.2.3 Workload Classification (Besta et al.)
- Point queries: minimal graph access, optimized with indices on labels/properties
- Neighborhood: accessing node's in- or out-neighborhood, optimized with sequential access
- Traversals: selection on neighborhood queries, inherently random
- Analytics: access all/most nodes and edges, optimized with sequential access to neighborhoods
- Key principle: data structures providing sequential access to vertices and neighborhoods are common optimization target

<span style="color:rgb(192, 0, 0)">> <b>[CANDIDACY content not on main]</b>: The candidacy background also lists benchmark suites in this section: LDBC (SNB, Business Intelligence), LDBC Graphalytics, GAP Benchmark. On main, benchmarks are introduced in the Evaluation chapter instead. Where should I put this?</span>

### 2.3 Graph Representations **[BOTH]**

#### 2.3.1 Adjacency Lists
- One row per vertex containing list of neighbors
- In-neighborhood and out-neighborhood maintained separately
- Memory: O(|V| + |E|); insertion: unsorted O(1) amortized, sorted O(log n)
- Sequential within single neighborhood; full-graph scans incur pointer-chasing overhead

<span style="color:rgb(192, 0, 0)">> <b>[CANDIDACY content not on main]</b>: Candidacy also discusses adjacency matrices (O(V^2) space, sparse for real-world graphs). I think we can bring that back to the dissertation.</span>

#### 2.3.2 Compressed Sparse Row (CSR)
- Compact, immutable data structure using two flat arrays: vertices and edges
- O(1) seeks, sequential scan of both vertex set and node neighborhoods
- Memory: O(|V| + |E|)
- Limitation: immutable; every modification requires reconstructing edge array
- Research on dynamic CSRs: NetworKit, Packed CSR, CSR++, LLAMA

#### 2.3.3 Persistent Graph Representations **[MAIN]**
- Real-world graphs exceed available memory; need persistent on-disk representations
- Disk I/O operates on fixed-size blocks; persistent representations must be block-based
- In-memory data structures not block-based; converting is non-trivial
- Approaches: LLAMA (persistent CSR on SSDs), reserved space (NetworKit, Packed CSR), batched updates, multi-versioning and delta updates

#### 2.3.4 Memory-Mapped I/O Considerations **[MAIN]**
- mmap maps file contents into process address space
- Fundamental problem: crash-consistent databases must control when dirty pages reach disk (WAL record before data page)
- With mmap: OS can flush dirty pages anytime -> incompatible with correct crash recovery
- Additional problems: I/O stalls from transparent page eviction, page-table contention
- Some systems use it (LiveGraph, KuzuDB) but acknowledge need for managed page cache

### <span style="color:rgb(192, 0, 0)">2.4 WiredTiger basics [TODO; estimate: 1 day ]</span>
- Introduce WT features we rely on
- Introduce connections, sessions, cursors, and transactions.
- Single-process, multi-threaded design. Each thread gets it's own session.
- Snapshot isolation and mention that writes can only occur at snapshot isolation. Reads can be done at Read-Committed/Read-Uncommitted
- WT_CACHE
- In-memory skip lists
- Reconciliation

> <span style="color:rgb(192, 0, 0)">The WiredTiger section is new. I think we should have a dedicated section here to avoid having to do inline explanations in the architecture/eval section. [DECIDE]</span>
---
## Chapter 3: Related Work and Design Space [Estimate: 1 day]

> Merged chapter. Uses the design space taxonomy (property vs. structural, static vs. dynamic, transaction support) as the organizing skeleton, with specific systems discussed as exemplars of each design point. Ends with a distillation positioning FlexoGraph.

### 3.1 Property Graphs vs. Structural Graphs **[CANDIDACY]**
- Property graph represents ground truth; structural graph derived from it
- Static structural graphs: materialized as-needed or periodically (e.g., Facebook's Unicorn)
- Dynamic structural graphs: updated as property graph changes
- Two classification features: (1) property vs structural, (2) static vs dynamic
  
### 3.2 Static Graph Processing Systems **[CANDIDACY]**
- Focus: graph analytics and mining tasks
- Key property: no consistency requirement between snapshots; batch ETL
- Preprocessing step: most time-consuming (GraphChi example: longer to preprocess than to run Triangle Counting or PageRank)

#### 3.2.1 In-Memory Graph Processing Systems [CANDIDACY + Paper]
- Shared-memory multicore: Gemini, GraphMat, Ligra, Galois, GPOP, GraphLab
- Distributed: GraphX, Pregel, PowerGraph, PowerLyra
- Problem: high communication overheads in distributed (McSherry 2015)
- **GAPBS** (reference implementations on CSR): FlexoGraph adapts GAP Benchmark Suite to use FlexoGraph API for fair comparison
- **Ligra**: direction-optimizing traversal (sparse/dense mode switching)
- **Galois**: priority-driven scheduling for irregular parallelism
- **Gemini**: chunk-based partitioning with locality-aware execution
- All require offline preprocessing to build in-memory layout; FlexoGraph comparison includes preprocessing time

#### 3.2.2 Out-of-Core Graph Processing Systems
- Cache frequently accessed data in memory, spill rest to disk
- On-disk layout leverages sequential access to minimize I/O
- Examples: GraphChi, X-Stream, GridGraph, V-part, Wonderland, CLIP, FlashGraph, Blaze
- **GraphChi**: Parallel Sliding Windows partitioning
- **X-Stream**: streaming unordered edge lists in scatter-gather model
- **Blaze**: NVMe-targeted partition-centric processing with I/O scheduling
- All require preprocessing, batch-only (no mutations during processing)
- FlexoGraph relies on WT buffer pool for spilling; competitive without dedicated I/O framework
### 3.3 Programming and Computation Models **[BOTH]**

#### 3.3.1 Computation Models
- Bulk Synchronous Parallel (BSP): supersteps with computation + communication (Pregel, Giraph)
- Asynchronous: no supersteps, updates visible immediately (GraphChi, GRACE)
- Gather-Apply-Scatter (GAS): three phases (GraphLab, PowerGraph, GraphX)

#### 3.3.2 Programming Models
- Vertex-centric, edge-centric, partition-centric
- Orthogonal to computation models
- FlexoGraph provides flexible API for any programming model

<span style="color:rgb(192, 0, 0)">> [DECIDE]: I think the discussion on Programming and Computation Models does not contribute anything the way it's currently written up. I need to revise this, or drop it entirely. </span>

### 3.4 Dynamic Graph Processing Systems **[BOTH]**

#### 3.4.1 Fast But No Consistency
- Updates applied directly without versioning (STINGER)
- Ongoing queries see updates immediately -> incorrect results

#### 3.4.2 Versioned Graphs
- New version per update with timestamps (GraphOne, LLAMA, ASPEN)

#### 3.4.3 Batched Updates
- Apply updates together; incremental algorithms minimize redundant computation (GraphBolt, Kickstarter, GraphIn, Tornado)

#### 3.4.4 Transactional Interface
- ACID guarantees (LiveGraph, Sortledton, Teseo)
- Most sophisticated consistency model
- **Teseo**: edges in fat-tree of dense pages, periodically rebalanced
- **GraphOne**: append-only edge log + adjacency array, blind-write semantics, no conflict detection
- **LiveGraph**: transactional edge log with mmap-backed adjacency-list snapshots; closest to FlexoGraph in scope
- **Sortledton and GTX**: <span style="color:rgb(192, 0, 0)">same features, but much much faster than even Teseo. I don't compare against them because Teseo is a more established baseline (also tree-based index). Worth mentioning</span>

### 3.5 Graph Analytics on Relational Systems **[MAIN]**
- TAO, Oracle PGX, DuckPGQ, GART
- Route analytics through separate in-memory engine or transient representation
- **Welc et al.**: SQL-based shortest paths competitive with Neo4j but degrade for iterative workloads
- **Hong et al.**: Green-Marl to distributed Giraph compilation, doesn't eliminate data movement
- FlexoGraph advantage: persistent analytics-friendly layouts in transactional KV store, no data movement

### 3.6 Graph Databases **[MAIN]**
- **Neo4j** (native graph storage, index-free adjacency), **ArangoDB** (multi-model document store), **JanusGraph** (distributed, pluggable backends), **OrientDB**, **PostgreSQL**
- **AsterDB** evaluation artifact
- LDBC SNB queries also compared against NeuG

### 3.7 Distillation of the Design Space **[BOTH]**
- Three classification features: (1) property vs structural, (2) static vs dynamic, (3) transaction support
- Grid showing all combinations; not all make sense (static systems don't need transactions)
- Graph databases = most general class (property graphs, transactions, consistency)
- FlexoGraph positioning: general-purpose system supporting all specialized use cases without data movement

---
## Chapter 4: Structural Graph Storage [Estimate 2 days]

  > First of two architecture chapters. Covers design principles, WiredTiger foundation, structural representations, topology cursors, partitioning, and bulk loading.

### 4.1 Design Principles **[MAIN]**
- Core principle: store structure independent of properties/labels (different layout optimizations needed)
- Persistence layer: WiredTiger chosen for non-blocking multi-threaded reads, ACID-compliant MVCC, scales beyond RAM
- Transaction model: single-process, multi-threaded; each thread opens private session; writes use snapshot isolation

> **[DECIDE]**: Candidacy has a section "What should a Graph Database Provide?" that frames the requirements more explicitly: (1) storage formats for high-performance analytics, (2) high-level API abstracting data structures, (3) framework for efficient operations (iterators, neighborhood collection). Should I bring this back?

### 4.2 Data Encoding **[BOTH]**
- Vertex IDs: 64-bit unsigned integers (big-endian 8-byte blobs)
- Degree counts: 32-bit unsigned integers
- Edge weights: double-precision floats (per Graphalytics spec)
- Big-endian encoding ensures WT's lexicographic comparison coincides with numeric order

### 4.3 Adjacency List Representation **[BOTH]**
- Two adjacency tables for in- and out-neighborhoods (adjlistin, adjlistout)
- Key: big-endian vertex ID; Value: packed byte blob (degree + neighbor IDs)
- WT_MODIFY API: modifies adjacency lists via change records (offset, length, replacement) stored in cache/WAL instead of rewriting entire list
- Undirected graphs: single table, each edge stored as two directed entries
- Read-optimized mode: separate node table storing in-degree and out-degree
- Weighted graphs: separate edge table with composite key (src, dst)

### 4.4 EdgeKey Representation **[BOTH]**
- Single sorted B-tree keyed by (src_id, dst_id)
- Sentinel design: reserved destination ID (0) marks vertex entries
- Node entry value: serialized in_degree and out_degree (read-optimized) or 1-byte dummy (write-optimized)
- Edge entry value: edge weight (weighted) or 1-byte sentinel (unweighted)
- Lexicographic key order ensures each node entry precedes its outgoing edges
- Out-neighborhood scan: position cursor at (src_id, 0), iterate keys with prefix src_id
- ID shifting: reserved 0 for sentinels; user IDs shifted +1 on insert, -1 on retrieval
- Directed graphs: two edge tables (edge_out keyed on (src, dst), edge_in keyed on (dst, src))
- Topology encoded entirely in keys; structural traversal never calls get_value()

### 4.5 Representation Comparison **[MAIN]**
- AdjList strengths: full neighborhood in single blob, fast sequential read in one I/O
- AdjList weaknesses: edge insertions require read-modify-write, concurrent insertions to same vertex contend
- EdgeKey strengths: topology in keys (no value deserialization), each edge insertion independent, no contention
- EdgeKey weaknesses: full neighborhood requires scanning multiple B-tree entries

### 4.6 Graph API and Topology Cursors **[BOTH]**
#### 4.6.1 Two-Layer API Design
- GraphEngine: owns WT connection, manages checkpoints, handles partitioning; creates GraphBase handles
- GraphBase: abstract class with virtual methods for node/edge manipulation and property access
- AdjList and SplitEdgeKey provide concrete implementations; application code is layout-agnostic

> **[DECIDE]**: Candidacy includes a full table of 20+ API operations (add/delete nodes and edges, degree queries, iterator functions, metadata functions, management functions). Main describes the API in prose. Update and rewrite.
#### 4.6.2 Topology Cursors
- Four abstract cursor classes: OutCursor, InCursor, NodeCursor, EdgeCursor
- AdjList cursors: deserialize packed neighbor blob from adjacency table
- EdgeKey cursors: iterate successive keys in edge B-tree
>**[TODO]** <span style="color:rgb(192, 0, 0)">The candidacy doc has class diagrams and code samples that walks the reader through the API design. Should I include that here?</span>
#### 4.6.3 Partitioning for Parallel Analytics **[MAIN]**
- GraphEngine pins read-only checkpoint, divides vertex set into disjoint key ranges
- Three strategies:
	- NODE_COUNT: equal-sized partitions by node count
	- EDGE_AWARE (default): partition by accumulated out-degree (balances work for degree-skewed graphs)
	- NODE_COUNT_FINE: finer-grained for work-stealing schedulers
- get_work_chunks(chunk_size): returns vector of small fixed-size key ranges for task-queue parallelism
>[TODO]: I <span style="color:rgb(192, 0, 0)">i need to rework this section a bit to explain the cost of these strategies and which algorithm uses which strategy.</span>
### 4.7 Bulk Loader **[CANDIDACY -- not on main]**
> **[CANDIDACY content not on main]**: This entire section exists only on the candidacy branch. A LOT has changed since then and it needs to be largely written from scratch.
#### 4.7.1 Preprocessing Pipeline
- Sort edges numerically with GNU sort (parallel options)
- Split edge list into shards matching core count
- Count unique nodes with uniq/wc
- Reverse edges, sort, split
- Build adjacency lists per thread
- Merge split adjacency lists
> I don't do these steps anymore. I wrote C programs to do all of these steps in parallel.
#### 4.7.2 Transactional Loader
- Uses standard WT cursor methods
- Multithreaded with separate session per thread
- Simpler but slower

#### 4.7.3 Standard Bulk Loader 
- uses WT bulk cursors
- There can only be one thread writing.
#### 4.7.3 Modified WiredTiger Bulk Loader
- Custom extension to WT infrastructure
- Creates leaf pages in B-tree, modifies reconciliation logic for internal nodes
- Multithreaded -- no internal page locks needed
- Based on WT 3.2.1, but works since page layout is same between v3.2.1 and v11.0.0
- Attribution: Keith Bostic implemented this modification

---
## Chapter 5: Property Graph Storage [Estimate: 2 days]
> Second architecture chapter. Builds on the structural storage foundation from Chapter 4. Covers why property storage is a distinct problem, label encoding, embedded and columnar storage modes, and property cursors. The API introduced in Chapter 4 is extended here with property access.
### 5.1 Why Property Storage Is a Separate Problem **[TO WRITE / expand from BOTH]**
- Structural storage optimizes for topology traversal: sequential access to neighborhoods, fast degree lookups
- Property storage optimizes for attribute access: point lookups on a single vertex's attributes, columnar scans across many vertices
- Different access patterns demand different physical layouts
- Co-locating properties with structural data creates write amplification (every degree update rewrites property blob)
- Separating them requires extra I/Os for queries that need both
- This tension motivates offering both embedded and columnar modes

### 5.2 Label Encoding **[EXPAND]**
#### 5.2.1 Design Alternatives
- Duplicating representations (per-label graph views): separate representation per vertex type; not scalable, requires cross-table queries
- Embedding attributes (type attribute stored with data): store source-type/destination-type with edges; requires full neighborhood scans to filter
- Vertex Relabelling: embed the vertex label information in the ID. The relabelled vertex IDs correctly disambiguate Person ID 1 and Post ID 1. We rely on the fact that src/dst types uniquely identify a label type (true for LDBC. This is not true for FinBench AFAIK)
#### 5.2.2 Labeled Vertex IDs (chosen approach) **[BOTH]**
- Partition vertex ID space by type: top 8 bits = label tag, remaining 56 bits = label-local ID
- O(1) label extraction via bit shift
- Big-endian storage in WT groups same-label vertices contiguously in B-tree
- Edge labels determined implicitly from endpoint labels
- Comparison with TuGraph (label in value) and GraphflowDB (consecutive ID ranges)
> **[CANDIDACY]**: Candidacy presents the three label-storage alternatives as a design-space discussion with tradeoffs. Main jumps directly to the chosen approach (labeled vertex IDs) without discussing alternatives. 

### 5.3 Embedded (Inline) Property Storage **[NEEDS TO BE EXPANDED]**
- EdgeKey: vertex properties appended after degree bytes in sentinel entry
- AdjList: properties in separate node_props and edge_props tables (due to WT_MODIFY constraint: WT_MODIFY requires value_format=u (untyped) -> cannot use typed columns)
- Write amplification cost (EdgeKey): every degree update rewrites full sentinel row including property blob
- Efficient when queries access most attributes of a vertex; better for multi-hop traversals with property filters
### 5.4 Columnar Property Storage **[NEEDS TO BE EXPANDED]**
- Per-label property tables using WT column groups
- Each column group physically stored as separate B-tree
- Example (LDBC SNB Person): temporal (creationDate, birthday -- 16 B/row), name (firstName, lastName, gender), contact (browserUsed, locationIP)
- Principle: separate fixed-size, scan-friendly columns from variable-length ones
- Both structural representations use same per-label tables in columnar mode
- Novel contribution: first system to provide disk-based columnar property access on a graph storage engine
- Multi-valued attributes: secondary tables with composite keys (vertex_id, index)
### 5.5 Choosing Between Modes **[MAIN]**
- Point queries: similar performance
- Multi-hop with property access: embedded wins (co-located data, fewer I/Os)
- BI scans: columnar wins (reads only relevant columns)
- Deployment strategy: choice can be per-label based on workload

### 5.6 Property Cursors **[MAIN]**
- NodeProp and EdgeProp cursors exploit column-group layout
- Read individual columns via typed accessors (e.g., get_uint64(n))
- In columnar mode: reads only that group's B-tree pages
- In embedded mode: extracts field from property blob (by using byte offsets)
- GraphBase factory methods select implementation -> query code is mode-agnostic
- Extends the topology cursor architecture from Chapter 4

---
  
## Chapter 6: Evaluation -- Static Graph Analytics [Estimate: 1 day]
> Covers in-memory and out-of-core settings. Both use static structural graphs with FlexoGraph in read-only mode.
### 6.1 Experimental Setup **[MAIN]**

#### 6.1.1 Hardware

- Structural graph benchmarks: dual-socket AMD EPYC 7643 @ 2.30 GHz, 96 cores/192 threads, 2 TB RAM, 2 TB NAND Flash SSD
- Ubuntu 22.04 LTS, Linux 6.8.0, GCC 13.3.0, flags: -O3 -march=native -mtune=native
- Hyperthreading enabled
#### 6.1.2 Datasets
- Graphs ranging from Dota-league (61K vertices, 51M edges) to Graph500-30 (448M vertices, 17B edges)
- Sources: LDBC Graphalytics, Koblenz Network Collection, Graph500 generators

#### 6.1.3 Analytic Kernels
- BFS, PageRank (PR), Connected Components (CC/WCC), Triangle Counting (TC), SSSP
- From LDBC Graphalytics Benchmark / GAP Benchmark Suite
### 6.2 In-Memory Graph Analytics **[MAIN]**
#### 6.2.1 Systems Compared
- FlexoGraph (AdjList, mmap_all=true, cache=800GB), GAPBS (native CSR), Galois, Ligra, Gemini
- Docker containers, one NUMA node (96 threads)

#### 6.2.2 Preprocessing Time Comparison
- Time to convert edge list to each system's in-memory format
- FlexoGraph operates directly on persistent representation (no separate loading step)

#### 6.2.3 Algorithm Execution Time
- PageRank, Connected Components, BFS, Betweenness Centrality
- Datasets: com-friendster, graph500-26/28/30, twitter-mpi, uk-2007
#### 6.2.4 Total Time (Preprocessing + Execution)
- FlexoGraph outperforms Galois and Ligra on every dimension
- GAPBS and Gemini faster on kernel runtime alone, but FlexoGraph competitive when including ingest time
- Ligra uses ~3x graph size in memory, causing OOM on graph500-30
#### 6.2.5 Peak Memory Usage
- Gemini most memory efficient; GAPBS relatively efficient
- FlexoGraph avoids costly ETL by running directly on persistent representation

### 6.3 Out-of-Core Graph Analytics **[MAIN]*
#### 6.3.1 Systems Compared
- FlexoGraph, GraphChi, X-Stream, Blaze
- Memory cap: 50% of graph's raw on-disk edge-list size; swap disabled

#### 6.3.2 Kernel Execution Time
- PageRank, Connected Components
- Datasets: twitter-mpi, graph500-26/28, com-friendster, uk-2007
- FlexoGraph outperforms all except Blaze on kernel execution
- Blaze 9-46% faster on synthetic graphs (CC), 31-37% faster (PR)
- FlexoGraph outperforms Blaze on real-world graphs (9% Twitter, 17% uk-2007, 65% com-friendster)

#### 6.3.3 Preprocessing Time Impact
- With preprocessing included: FlexoGraph 1.3x to 6.5x faster than any other system
- Preprocessing often dominates end-to-end time (log-scale Y axis)
#### 6.3.4 I/O Bandwidth Analysis
- iostat traces comparing I/O profiles
- FlexoGraph: 410 MB/s average (76% of peak 540 MB/s), flat profile
- X-Stream: sawtooth pattern, 480 MB/s peak, 330 MB/s average
- Blaze: 109 MB/s average, diminishing over time
- GraphChi: 43 MB/s (8% of peak), random access penalty

---
## Chapter 7: Evaluation -- Dynamic Structural Graphs [Estimate 1 day + 5 days for concurrent experiment/analysis]

> Covers insertion throughput, mixed workloads, and post-ingestion analytics on dynamic structural graphs.
### 7.1 Experimental Setup **[MAIN]**
- Systems compared: Teseo, LiveGraph, GraphOne, FlexoGraph (EdgeKey and AdjList)
- GFE driver used for fair benchmarking

### 7.2 Insertion Scalability **[MAIN]**
- Dataset: graph500-24
- Variable: writer threads (1-72)
- Results: GraphOne peaks at 6.3M edges/s (40 threads), Teseo 5.1M edges/s (72 threads), LiveGraph plateaus at 0.49M edges/s, FlexoGraph EdgeKey 1.7M edges/s (72 threads), FlexoGraph AdjList 0.77M edges/s (48 threads)

### 7.3 Ingest and Update Throughput **[MAIN]**

#### 7.3.1 Insertion-Only
- 6 datasets, 51M to 1.05B edges
- GraphOne: 5.6-6.6M edges/s, Teseo: 4.3-5.5M edges/s, FlexoGraph EdgeKey: 1.2-1.8M edges/s (3-5x slower due to persistence), LiveGraph: 0.48M edges/s

#### 7.3.2 Mixed Insert/Delete Workloads

- 2.6B operations, 55% insert / 45% delete on graph500-24
- Teseo: 7.0M ops/s; GraphOne collapses to 0.05M ops/s (115x drop, tombstone overhead); FlexoGraph EdgeKey: 1.06M ops/s; LiveGraph: 0.42M ops/s

#### 7.3.3 Layout Tradeoff Analysis
- EdgeKey: one B-tree row per edge, independent inserts, zero transaction aborts, scales to 72 threads
- AdjList: one record per vertex, high conflicts on power-law graphs, caps at ~0.8M edges/s

### 7.4 Post-Ingestion Analytics **[MAIN]**
- Datasets: graph500-22/24/26 (uniform and Kronecker variants)
- Kernels: BFS, PageRank, WCC
- FlexoGraph AdjList: only system delivering fast, stable performance across all kernels/graphs
- Teseo: fastest BFS but PageRank/WCC degrade sharply
- GraphOne: fastest inserter but WCC collapses at scale
- FlexoGraph EdgeKey: orders of magnitude slower on analytics than AdjList
- Key finding: layout choice is the dominant factor in analytical performance

### <span style="color:rgb(192, 0, 0)">7.5 Concurrent Insertions + Analytics [TODO - 5 days]</span>
- run analytics while insertions are underway
- Key idea: uncover the relationship between checkpointing, rate of insertion, and reader:writer ratio.
- Might need some experiments 

---
## Chapter 8: Evaluation -- Property Graph Workloads [Estimate: 2 days]

### 8.1 Experimental Setup **[MAIN]**
- Hardware: Intel Xeon W-2275 @ 3.30 GHz, 14 cores/28 threads, 128 GB RAM, 1 TB NVMe SSD
- Integration: AsterDB evaluation artifact with Apache TinkerPop Gremlin traversal language
- FlexoGraph configs: 4 combinations (AdjList/EdgeKey x embedded/columnar)
- Comparison systems: Neo4j, ArangoDB, NeuG, AsterDB, OrientDB, JanusGraph, PostgreSQL (SQLG)

### 8.2 Query Implementation Methodology **[TODO ]**

> Describes how LDBC SNB queries were implemented against FlexoGraph's cursor-based API using LLM-assisted code generation.

- Problem: FlexoGraph has no query engine or query language; evaluation against systems with full query engines (Neo4j/Cypher, ArangoDB/AQL) requires imperative C++ implementations of each benchmark query
- Approach: spec-driven query logic synthesis using an LLM
1. Provided the LLM with the LDBC SNB query specifications and FlexoGraph source code
2. Generated schema interfaces: mapping LDBC entity types and relations to FlexoGraph's labeled vertex ID space and property tables via the API
3. Generated query implementations: C++ code executing each LDBC query using FlexoGraph's cursor-based API
- Verification: query results compared against the same queries executed on Neo4j to validate correctness
- Rationale: for novel storage systems without a query engine, LLMs can generate the glue code needed for evaluation against more mature systems; the query logic was systematically derived from the same spec that other systems implement through their query planners, not hand-tuned

### 8.3 LDBC Social Network Benchmark Schema **[MAIN -- reframed from old Ch 5]**
- Dataset: LDBC SNB Scale Factor 3 (~800K vertices, ~3.5M edges, 4 entity types, 7 relation types)
- Vertex types: Person, Post, Comment, Forum (and others in SNB)
- Edge types: knows, likes, hasCreator, containerOf, etc.
- Property schemas per label (e.g., Person: firstName, lastName, birthday, creationDate, browserUsed, locationIP, gender, emails, languages)
- Fixed-size vs. variable-length properties
- Multi-valued attributes (e.g., set of email addresses)

### 8.4 Graph Algorithms on Property Graphs **[MAIN]**

- Dataset: cit-Patents (3.77M vertices, 16.5M edges)
- Algorithms: PageRank, Community Detection (CDLP), WCC, BFS, Shortest Path
- FlexoGraph AdjList: 1000x faster than Neo4j on PageRank (0.32s vs 429s), 8000x vs OrientDB
- WCC: 3000x faster than Neo4j
- Per-call overhead analysis: 50% of Neo4j PageRank time is Gremlin overhead (34%) + index resolution (16%)

### 8.5 LDBC SNB Query Performance **[MAIN]**

#### 8.5.1 Point Queries
- R1 (Person properties): FlexoGraph 7.28 us, Neo4j 28.4 us (3.9x), ArangoDB 19.8 us
- X1 (Post properties): FlexoGraph 6.05 us, Neo4j 22.1 us

#### 8.5.2 Aggregate Queries
- A2 (count knows): FlexoGraph 12.8 us, Neo4j 66.2 us, ArangoDB 38.4 us
- A3 (count likes): FlexoGraph 13.8 us, Neo4j 82.3 us
- X5 (count incoming): columnar 7.68 us vs embedded 10.2 us

#### 8.5.3 Multi-Hop Traversals
- X3: FlexoGraph 0.24 ms, Neo4j 13.1 ms (56x)
- IC-3 (friends-of-friends): NeuG 3.84 ms, Neo4j 8.3 ms, FlexoGraph 29.0 ms (reversed ranking -- FlexoGraph slower here)
- IC-9 (friends' messages): FlexoGraph 1.47 ms, Neo4j 64.5 ms (44x)

#### 8.5.4 BI Scans
- BI-1 (scan posts by year/length): FlexoGraph columnar 0.40s, Neo4j 1.78s (4.4x), ArangoDB 6.67s
- BI-12 (top creators): NeuG 0.09s, FlexoGraph 1.24s, Neo4j 2.66s

#### 8.5.5 Write Operations
- W1 (insert person): ArangoDB 21.3 us, Neo4j 26.2 us, FlexoGraph 110 us (FlexoGraph slower)
- W2 (insert knows): ArangoDB 26.9 us, Neo4j 30.9 us, FlexoGraph 165 us
- X4 (insert likes): FlexoGraph 11.3 us, Neo4j 37.4 us (FlexoGraph faster)

### 8.6 Embedded vs. Columnar Tradeoff **[MAIN]**
- Point queries: similar performance
- Multi-hop with properties: embedded wins (IC-9: 1.47 ms vs 17.7 ms, 12x)
- BI scans: columnar wins
- Deployment strategy: per-label choice based on workload

### 8.7 Microbenchmarks Against Graph Databases **[WRITTEN BUT NOT INCLUDED IN PAPER]**
- 100K single-threaded operations per measurement
- Datasets: DBLP (~317K vertices), Wikipedia (~1.87M vertices)
#### 8.7.1 Structural Operations
- Get neighbors: FlexoGraph 1.17 us, Neo4j 11.67 us (10x), AsterDB 31.42 us (27x)
- Vertex insert: FlexoGraph 1.88 us, Neo4j 8.75 us (4.7x)
- Document-oriented systems (ArangoDB, OrientDB): 3-4 orders of magnitude slower

#### 8.7.2 Property CRUD Operations
- Vertex property update: FlexoGraph ~10 us, Neo4j 46.7 ms, JanusGraph 105.8 ms (3-4 orders of magnitude difference)
- Vertex property search: FlexoGraph 14.4 ms, AsterDB 303 ms (21x), Neo4j 425 ms (29x)
- Key finding: direct B-tree cursor operations vs. query engine overhead

---
## Chapter 9: Future Work **[TO WRITE; Estimate: 1 day]**

### 9.1 High-Level Query Language Integration **[MAIN]**
- FlexoGraph currently exposes only a C++ cursor API; no declarative query language
- Natural target: GQL (ISO standard) or openCypher compilation down to cursor-level operations
- Challenge: query planning and optimization without a traditional catalog or cost model
- Connection to the LLM-based synthesis in Chapter 8: could an LLM-assisted approach serve as a stopgap or inform the design of a query planner?
  
### 9.3 Learned Indexes and Adaptive Layout Selection **[TO WRITE]**
- FlexoGraph's thesis is that data layout is the key performance determinant; currently the user manually selects layout and property mode
- Natural extension: the system observes query workload and data distribution and adapts automatically
- Concrete decision points amenable to learned optimization:
- AdjList vs. EdgeKey selection based on observed read/write ratio and degree distribution
- Embedded vs. columnar property mode based on which properties are co-accessed by queries
- Column group composition (which properties share a B-tree) based on query co-access patterns
- Cursor prefetching hints based on learned traversal patterns
- Connects directly to Chapter 5's argument that mode choice should be per-label based on workload; learned indexes are the automated version of that manual decision
- Related work: learned index structures (Kraska et al.), SageDB, Bao (learned query optimization)

### 9.4 Graph Storage for Machine Learning Workloads **[TO WRITE]**
- GNN training and inference impose specific demands on graph storage that current practice handles with ad hoc solutions (DGL/PyG custom storage, separate graph sampling services)
- FlexoGraph's design maps onto these requirements concretely:

#### 9.4.1 Training: Neighborhood Sampling on Large Graphs
- GNN training (GraphSAGE, GAT) requires repeated neighborhood sampling across mini-batches
- Current practice: load entire graph into memory or use framework-specific storage
- For graphs exceeding memory, FlexoGraph's out-of-core capability with snapshot-consistent neighborhood iterators is directly applicable
- Columnar property mode aligns with training access patterns: scan a single feature column (node embeddings, edge weights) across many vertices per mini-batch
- Snapshot isolation provides consistent training data without blocking concurrent graph updates
#### 9.4.2 Inference: Low-Latency Neighborhood Lookups on Live Graphs
- Real-time GNN inference (fraud detection, recommendation) requires low-latency neighborhood lookups on a mutating graph
- This is the HGTAP use case: transactional writes proceed while inference queries read consistent snapshots via MVCC
- FlexoGraph's property cursors provide the feature vectors needed for inference without a separate feature store
  
#### 9.4.3 Open Problems
- Language bridge: FlexoGraph has a C++ API; ML frameworks are Python — bridging via pybind11, shared-memory interface, or a serving protocol is a concrete engineering problem
- Batched sampling: training requires batches of multi-hop neighborhoods; current iterator API is single-traversal — a batched sampling primitive would reduce cursor overhead
- Feature materialization: pre-computing and caching derived features (e.g., aggregated neighbor embeddings) as materialized views in the property layer

  

---
## Chapter 10: Conclusion

### 10.1 Summary of Contributions **[MAIN]**
- FlexoGraph: graph database on WT storing graphs in persistent, analytics-friendly layouts
- Runs whole-graph analytics directly, eliminating ETL/preprocessing
- Two structural representations (AdjList, EdgeKey) with complementary read/write tradeoffs
- Typed property storage: embedded and columnar modes with disk-based per-column I/O isolation on transactional B+ tree
### 10.2 Key Results **[MAIN]**
- Matches most in-memory graph processing systems on end-to-end analytics
- Sustains stable throughput under mixed insert-delete workloads
- Property graph queries orders of magnitude faster than Neo4j, ArangoDB, JanusGraph
### 10.3 Tradeoffs **[MAIN]**
- FlexoGraph trades peak insertion throughput for persistence and ACID guarantees
- Teseo and GraphOne 3-5x faster on pure insertion (lightweight in-memory write paths)
### 10.4 Central Lesson **[MAIN]**
- Carefully designed persistent layout on mature storage engine can serve both OLTP and OLAP graph workloads competitively, without separate analytics engine or data movement


---
## Appendix

### A. Algorithm Implementations Using FlexoGraph API **[CANDIDACY -- PageRank; TO WRITE for others]**
- PageRank implementation using GraphAPI (C++ code listing with OpenMP, NodeCursor, InCursor)
- **[DECIDE]**: Which algorithms to include? (BFS, PageRank, WCC, SSSP?)  

> **[CANDIDACY content not on main]**: The candidacy doc includes a full PageRank implementation listing (appendix:pagerank_graphapi) showing OpenMP parallelization, cursor usage.