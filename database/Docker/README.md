
# Creation of a container with Neo4j database

The following commands are for creating a Neo4j container with a part of the northwind database data.

### Create container:

<span style="color:grey">docker run --name northwindneo4j -p7474:7474 -p7687:7687 -d -v C:\##INSERT_MOUNT_PATH##:/var/lib/neo4j/import --env NEO4J_AUTH=neo4j/password neo4j:latest
</span>

<span style="color:grey">##INSERT_MOUNT_PATH##</span> is a placeholder for a file path on your own hard drive that is to be mounted, there the CSV files can then be copied in.
These files are then available within the container in the directory path "/var/lib/neo4j/import".

### Populate Database:
After starting the docker container and navigating to the "/import" folder, there should be all csv files. 
You can then just run all commands from the "populate_cypher_commands.txt" file to create nodes and relationships.
After that the database should be ready to use.

### Start database console:
cypher-shell -u neo4j -p password

When starting for the first time, the password and the username must be set after entering the cypher-shell.
By default, both are "neo4j".


