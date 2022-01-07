# introduction
The project is taken in Distributed System course in university of stuttgart which is taught by Prof. Dr. Marco Aiello. The end deliverable of project to implement,
 1. Archtiecture Design
 2. Dynamic Discovery of Host aka maintaining group of multicast group
 3. Crash fault tolerance
 4. Reliable ordered multicast
 5. Proven voting 
 6. Byzantine failure 

# Project Description

our project goal was to implement replicated key-value store database which provide basic key value operation like read,delete,update,write e.g. In project,we had 3 main componenet which interact with each other, client library which will be used by end user, cordinator which is middle man between client and replicatd store. For replicated data store, we implement active replication as it can handle many failure and scalable without much headache. For cordinator, we implement bully election protocol. All operation of client pass through cordinator. We utilize replica store to store state of leader in replia, incase of one leader crash other will take over. we implement crash failure aka fail stop failure both at cordinator level and replica level. we also handle different type of failure in client library e.g client won't be effected if leader cordinator went down and another take over. All the dirty work of establishing connection and finding leader is handled in client library. At cordniator level we implmenet groupview logic to keep coridinator uptodate to fellow cordinator. At last, we implemnt total order reliable multicast in replica and utilize same for cordinator operation.

