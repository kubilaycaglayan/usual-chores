Add themed seed data for the household chores MVP.

Requirements:

Create several public seeded households. Each household should contain:

* A clear theme/name
* 4–8 famous fictionalized/persona-style members related to that theme
* 8–15 themed chores
* A mixture of open, claimed, completed, overdue, and recurring chores
* Realistic completion history so contribution statistics and fairness recommendations can be demonstrated
* At least 2 recurring chores using fixed schedules
* Optional deadlines on some chores
* Maximum 10 members per household

Initial households:

1. Scientists House
   Members can include Einstein, Marie Curie, Newton, Tesla, Darwin, Feynman.
   Example chores:

* Clean the laboratory
* Organize experiment notes
* Wash the glassware
* Restock chalk
* Take out radioactive waste
* Prepare coffee for the morning discussion

2. Movie Directors House
   Members can include Kubrick, Spielberg, Scorsese, Tarantino, Coppola, Hitchcock.
   Example chores:

* Organize the screening room
* Clean camera equipment
* Prepare movie-night snacks
* Sort the Blu-ray collection
* Take out trash after screening
* Vacuum the editing room

3. Writers House
   Members can include Dostoevsky, Virginia Woolf, Kafka, Orwell, Tolstoy, Hemingway.
   Example chores:

* Organize the library
* Make coffee
* Clean writing desks
* Water the plants
* Buy printer paper
* Take out recycling

4. Computer Scientists House
   Members can include Alan Turing, Ada Lovelace, Donald Knuth, Grace Hopper, Edsger Dijkstra, Margaret Hamilton.
   Example chores:

* Restart the router
* Organize cables
* Clean keyboards
* Back up the household server
* Empty the coffee machine
* Update the shared shopping list

Implementation requirements:

* Make the seed operation idempotent. Running it multiple times must not duplicate seeded households, users/personas, chores, or completion-history records.
* Clearly distinguish seeded personas from real registered users in the database.
* Seeded households must be public and visible through the same normal application flows as user-created households.
* Seeded chores must use the application's actual domain models and business rules. Do not create special demo-only data structures.
* Create enough historical completions that some members clearly have fewer completed chores than others, allowing the fairness recommendation feature to produce visible recommendations.
* Include examples where a recurring chore has previous completed occurrences and a currently open next occurrence.
* Include at least one overdue unclaimed chore and one overdue claimed chore.
* Use deterministic seed data instead of random values so development and tests remain reproducible.
* Keep the seed implementation easy to extend with additional themed households later.

After implementation, verify that the seeded data correctly appears in:

1. household discovery,
2. household member lists,
3. open/claimed/overdue chores,
4. recurring chores,
5. completion history,
6. contribution statistics,
7. fairness recommendations.

Do not add new product features while implementing this. Work within the existing MVP domain model.
