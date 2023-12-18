### Abstract (for the candidacy)
  
  What we want to say here:
  #### Large graphs exist and we need to store them
  * Graphs are the perfect struct to encapsulate a lot of connected data, and we are generating a lot more of such data. We need some way to store and process it.

  #### Lifecycle of a graph and where improvement is sought 
  * A significant amount of data comes ordered from a primary datastore (database). Maybe talk about the types of datastores the graphs can be extracted from. 
  * The types of analytics activity that is common on graph datasets - batch, interactive + exploratory, query, <-- find more.
  * This is just one aspect of the picture. There is also a need to store this data in a clean format that is amenable to analytics. 
   I think we need to break down requirements into feature groups (hierarchy of needs)
    - one set about what we need from the storage component that is used entirely during the ```get()``` calls during analytics
    - Metadata or transient state during execution
    - Concurrency model 
    - Versioning (is this independent of concurrency?)
    - The application layer requirements -- what we enable (attributes, structure only, programming API and ready to go algorithms, hooks for query execution engine?)
    - Achieve full HTAP capability
  
  #### Generality vs Specificity in Storage Engines:
  * The system that underpins any data-intensive system is a storage engine. Most systems custom-craft their system which works incredibly well for their specific usecases, but might not at all work for all the usecases that one might need in the future. 

  * Using a full-feature battle-hardened storage engine can make the system future and feature proof. Sure, performance and generality are often at odds, but such a system might be useful in its own right as a research vehicle to explore different processing semantics, datastructure choices, or features.

  * We want to ease the burden of development for future systems and by having an interface that allows easy extension. 
