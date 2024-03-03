import streamlit as st
from PyPDF2 import PdfReader
from nltk.corpus import wordnet
import requests
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
import re
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import auth_functions

# Download NLTK resources
nltk.download('vader_lexicon')
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('sent_tokenize')
nltk.download('word_tokenize')
nltk.download('FreqDist')
nltk.download('SentimentIntensityAnalyzer')

# Load the sentiment analysis pipeline
sia = SentimentIntensityAnalyzer()

# Function to summarize text using NLTK
def preprocess_text(text):
    words = word_tokenize(text.lower())
    stop_words = set(stopwords.words("english"))
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
    return filtered_words

# Function to summarize text using NLTK
def summarize_text(text):
    sentences = sent_tokenize(text)
    word_freq = FreqDist(preprocess_text(text))
    ranking = {}

    for i, sentence in enumerate(sentences):
        for word in word_tokenize(sentence.lower()):
            if word in word_freq:
                if len(sentence.split(' ')) < 30:
                    if i not in ranking:
                        ranking[i] = word_freq[word]
                    else:
                        ranking[i] += word_freq[word]

    total_length = sum(len(sentence) for sentence in sentences)
    target_length = total_length // 2

    summary_length = 0
    top_sentences_index = []
    for j in sorted(ranking, key=ranking.get, reverse=True):
        summary_length += len(sentences[j])
        # Exclude sentences starting with a number followed by a comma, space, or period
        if not re.match(r"^\d+[\.,\s]", sentences[j]):
            top_sentences_index.append(j)
        if summary_length >= target_length:
            break

    top_sentences = [sentences[j] for j in sorted(top_sentences_index)]
    return ' '.join(top_sentences)

# Function to extract text from a PDF
def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as f:
        reader = PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

# Function to retrieve content from Wikipedia
def retrieve_content(topic):
    # Wikipedia URL for the provided topic
    url = f"https://en.wikipedia.org/wiki/{topic}"

    # Send a GET request to the Wikipedia page
    response = requests.get(url)

    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the main content of the page
        main_content = soup.find(id='mw-content-text')

        # Extract text from paragraphs within the main content
        paragraphs = main_content.find_all('p')

        # Retrieve text from each paragraph
        content = [p.get_text() for p in paragraphs]

        return content
    else:
        return None

def get_word_definitions(word):
    synsets = wordnet.synsets(word)
    definitions = []
    for synset in synsets:
        definitions.append(synset.definition())
    return definitions

# Function to retrieve definitions from a hypothetical technical dictionary
def get_technical_definitions(word):
    # Define a simple dictionary of technical terms and their definitions
    technical_dictionary = {
        
        "algorithm": "A set of rules or instructions designed to solve a specific problem.",
        "API": "Application Programming Interface - a set of protocols, tools, and definitions that allows different software applications to communicate with each other.",
        "machine learning": "A branch of artificial intelligence that enables computers to learn from data and improve over time without being explicitly programmed.",
        "database": "A structured collection of data, typically stored and accessed electronically from a computer system.",
        "cloud computing": "The delivery of computing services—including servers, storage, databases, networking, software, analytics, and intelligence—over the Internet ('the cloud') to offer faster innovation, flexible resources, and economies of scale.",
        "cybersecurity": "The practice of protecting systems, networks, and programs from digital attacks.",
        "encryption": "The process of converting information or data into a code to prevent unauthorized access.",
        "artificial intelligence": "The simulation of human intelligence processes by machines, especially computer systems.",
        "virtual reality": "A simulated experience that can be similar to or completely different from the real world.",
        "blockchain": "A decentralized, distributed ledger technology that records transactions across multiple computers.",
        "Internet of Things (IoT)": "The network of physical devices, vehicles, home appliances, and other items embedded with electronics, software, sensors, actuators, and connectivity, enabling them to connect, collect, and exchange data.",
        "augmented reality": "An interactive experience of a real-world environment where the objects that reside in the real world are enhanced by computer-generated perceptual information.",
        "big data": "Extremely large data sets that may be analyzed computationally to reveal patterns, trends, and associations, especially relating to human behavior and interactions.",
        "deep learning": "A subset of machine learning that uses artificial neural networks with many layers (hence the 'deep') to model and analyze complex data.",
        "containerization": "A lightweight alternative to full machine virtualization that involves encapsulating an application in a container with its own operating environment.",
        "edge computing": "A distributed computing paradigm that brings computation and data storage closer to the location where it is needed to improve response times and save bandwidth.",
        "devOps": "A set of practices that combines software development (Dev) and information technology operations (Ops) to shorten the system development life cycle and provide continuous delivery with high software quality.",
        "agile methodology": "An iterative approach to software development that emphasizes flexibility, customer collaboration, and rapid and incremental delivery of working software.",
        "microservices": "A software development technique that structures an application as a collection of loosely coupled services, which are fine-grained and can be developed, deployed, and scaled independently.",
        "scalability": "The capability of a system, network, or process to handle a growing amount of work, or its potential to be enlarged to accommodate that growth.",
        "front-end": "The user interface and user experience layer of a software application or website that users interact with directly.",
        "back-end": "The server-side of a software application that is responsible for managing and processing data, as well as communicating with the front-end.",
        "API gateway": "A server that acts as an API front-end, receiving API requests, enforcing throttling and security policies, passing requests to the back-end service, and then passing the response back to the requester.",
        "container orchestration": "The automated arrangement, coordination, and management of containers and the services they contain.",
        "continuous integration": "The practice of regularly integrating code changes into a shared code repository, where automated builds and tests are run.",
        "continuous delivery": "The practice of automating the software delivery process so that code changes are automatically built, tested, and prepared for release to production.",
        "continuous deployment": "The practice of automatically deploying code changes to production or other environments after passing automated tests.",
        "RESTful API": "A type of API that adheres to the principles of Representational State Transfer (REST), making it easy to understand and use.",
        "GraphQL": "A query language for APIs and a runtime for executing those queries with existing data.",
        "serverless computing": "A cloud computing execution model where the cloud provider dynamically manages the allocation and provisioning of servers, allowing developers to focus on writing code without worrying about server management.",
        "distributed systems": "A collection of independent computers that appear to the users of the system as a single coherent system.",
        "version control": "The management of changes to documents, computer programs, large web sites, and other collections of information.",
        "dependency injection": "A technique in which an object receives other objects that it depends on (the dependencies) as constructor parameters or through setter methods.",
        "agile manifesto": "A set of guiding principles for software development, emphasizing flexibility, collaboration, and responsiveness to change.",
        "mocking": "The process of creating objects that simulate the behavior of real objects in controlled ways.",
        "binary search": "A search algorithm that finds the position of a target value within a sorted array.",
        "DNS": "Domain Name System - a hierarchical and decentralized naming system for computers, services, or other resources connected to the Internet or a private network.",
        "HTTP": "Hypertext Transfer Protocol - an application protocol for distributed, collaborative, hypermedia information systems.",
        "HTTPS": "Hypertext Transfer Protocol Secure - an extension of HTTP that is used for secure communication over a computer network.",
        "TCP/IP": "Transmission Control Protocol/Internet Protocol - the basic communication language or protocol of the Internet.",
        "SSL/TLS": "Secure Sockets Layer/Transport Layer Security - cryptographic protocols that provide secure communication over a computer network.",
        "firewall": "A network security device that monitors and controls incoming and outgoing network traffic based on predetermined security rules.",
        "load balancing": "The process of distributing incoming network traffic across multiple servers to ensure no single server bears too much demand.",
        "packet": "A unit of data transmitted over a network.",
        "metadata": "Data that provides information about other data.",
        "root cause analysis": "A method of problem-solving used for identifying the underlying causes of problems or issues.",
        "refactoring": "The process of restructuring existing computer code without changing its external behavior to improve its readability, maintainability, and efficiency.",
        "API documentation": "Instructions on how to effectively use and integrate with an API, including descriptions of API endpoints, parameters, and response formats.",
        "code review": "A systematic examination of source code intended to find and fix mistakes overlooked in the initial development phase, improving code quality and fostering collaboration.",
        "bug tracking": "The process of capturing, reporting, and managing bugs in software.",
        "agile sprint": "A short, time-boxed period during which a development team works to complete a set amount of work.",
        "Kubernetes": "An open-source container orchestration platform for automating deployment, scaling, and management of containerized applications.",
        "microcontroller": "A small computer on a single integrated circuit containing a processor core, memory, and programmable input/output peripherals.",
        "FPGA": "Field-Programmable Gate Array - a semiconductor device containing programmable logic components and programmable interconnects.",
        "API gateway": "A server that acts as an API front-end, receiving API requests, enforcing throttling and security policies, passing requests to the back-end service, and then passing the response back to the requester.",
        "container orchestration": "The automated arrangement, coordination, and management of containers and the services they contain.",
        "continuous integration": "The practice of regularly integrating code changes into a shared code repository, where automated builds and tests are run.",
        "continuous delivery": "The practice of automating the software delivery process so that code changes are automatically built, tested, and prepared for release to production.",
        "continuous deployment": "The practice of automatically deploying code changes to production or other environments after passing automated tests.",
        "RESTful API": "A type of API that adheres to the principles of Representational State Transfer (REST), making it easy to understand and use.",
        "GraphQL": "A query language for APIs and a runtime for executing those queries with existing data.",
        "serverless computing": "A cloud computing execution model where the cloud provider dynamically manages the allocation and provisioning of servers, allowing developers to focus on writing code without worrying about server management.",
        "distributed systems": "A collection of independent computers that appear to the users of the system as a single coherent system.",
        "version control": "The management of changes to documents, computer programs, large web sites, and other collections of information.",
        "dependency injection": "A technique in which an object receives other objects that it depends on (the dependencies) as constructor parameters or through setter methods.",
        "agile manifesto": "A set of guiding principles for software development, emphasizing flexibility, collaboration, and responsiveness to change.",
        "mocking": "The process of creating objects that simulate the behavior of real objects in controlled ways.",
        "binary search": "A search algorithm that finds the position of a target value within a sorted array.",
        "DNS": "Domain Name System - a hierarchical and decentralized naming system for computers, services, or other resources connected to the Internet or a private network.",
        "HTTP": "Hypertext Transfer Protocol - an application protocol for distributed, collaborative, hypermedia information systems.",
        "HTTPS": "Hypertext Transfer Protocol Secure - an extension of HTTP that is used for secure communication over a computer network.",
        "TCP/IP": "Transmission Control Protocol/Internet Protocol - the basic communication language or protocol of the Internet.",
        "SSL/TLS": "Secure Sockets Layer/Transport Layer Security - cryptographic protocols that provide secure communication over a computer network.",
        "firewall": "A network security device that monitors and controls incoming and outgoing network traffic based on predetermined security rules.",
        "load balancing": "The process of distributing incoming network traffic across multiple servers to ensure no single server bears too much demand.",
        "packet": "A unit of data transmitted over a network.",
        "metadata": "Data that provides information about other data.",
        "root cause analysis": "A method of problem-solving used for identifying the underlying causes of problems or issues.",
        "refactoring": "The process of restructuring existing computer code without changing its external behavior to improve its readability, maintainability, and efficiency.",
        "API documentation": "Instructions on how to effectively use and integrate with an API, including descriptions of API endpoints, parameters, and response formats.",
        "code review": "A systematic examination of source code intended to find and fix mistakes overlooked in the initial development phase, improving code quality and fostering collaboration.",
        "bug tracking": "The process of capturing, reporting, and managing bugs in software.",
        "agile sprint": "A short, time-boxed period during which a development team works to complete a set amount of work.",
        "Kubernetes": "An open-source container orchestration platform for automating deployment, scaling, and management of containerized applications.",
        "microcontroller": "A small computer on a single integrated circuit containing a processor core, memory, and programmable input/output peripherals.",
        "FPGA": "Field-Programmable Gate Array - a semiconductor device containing programmable logic components and programmable interconnects.",
        "database": "A structured collection of data, typically stored and accessed electronically from a computer system.",
        "cloud computing": "The delivery of computing services—including servers, storage, databases, networking, software, analytics, and intelligence—over the Internet ('the cloud') to offer faster innovation, flexible resources, and economies of scale.",
        "cybersecurity": "The practice of protecting systems, networks, and programs from digital attacks.",
        "encryption": "The process of converting information or data into a code to prevent unauthorized access.",
        "artificial intelligence": "The simulation of human intelligence processes by machines, especially computer systems.",
        "virtual reality": "A simulated experience that can be similar to or completely different from the real world.",
        "blockchain": "A decentralized, distributed ledger technology that records transactions across multiple computers.",
        "Internet of Things (IoT)": "The network of physical devices, vehicles, home appliances, and other items embedded with electronics, software, sensors, actuators, and connectivity, enabling them to connect, collect, and exchange data.",
        "augmented reality": "An interactive experience of a real-world environment where the objects that reside in the real world are enhanced by computer-generated perceptual information.",
        "big data": "Extremely large data sets that may be analyzed computationally to reveal patterns, trends, and associations, especially relating to human behavior and interactions.",
        "deep learning": "A subset of machine learning that uses artificial neural networks with many layers (hence the 'deep') to model and analyze complex data.",
        "containerization": "A lightweight alternative to full machine virtualization that involves encapsulating an application in a container with its own operating environment.",
        "edge computing": "A distributed computing paradigm that brings computation and data storage closer to the location where it is needed to improve response times and save bandwidth.",
        "devOps": "A set of practices that combines software development (Dev) and information technology operations (Ops) to shorten the system development life cycle and provide continuous delivery with high software quality.",
        "agile methodology": "An iterative approach to software development that emphasizes flexibility, customer collaboration, and rapid and incremental delivery of working software.",
        "microservices": "A software development technique that structures an application as a collection of loosely coupled services, which are fine-grained and can be developed, deployed, and scaled independently.",
        "scalability": "The capability of a system, network, or process to handle a growing amount of work, or its potential to be enlarged to accommodate that growth.",
        "cloud storage": "A service model in which data is maintained, managed, backed up remotely, and made available to users over a network (typically the Internet).",
        "cloud computing provider": "A company that offers cloud computing services, including infrastructure as a service (IaaS), platform as a service (PaaS), and software as a service (SaaS).",
        "data warehouse": "A system used for reporting and data analysis, considered a core component of business intelligence.",
        "database management system (DBMS)": "Software that manages databases, providing tools for creating, querying, updating, and administering databases.",
        "relational database": "A type of database that stores and provides access to data points that are related to one another, typically organized into tables with rows and columns.",
        "NoSQL database": "A type of database that provides a mechanism for storage and retrieval of data that is modeled in means other than the tabular relations used in relational databases.",
        "cloud database": "A database that is optimized or designed for a virtualized computing environment, typically offered as a service (DBaaS) over the Internet.",
        "database server": "A server that provides database services to other computer programs or computers, as defined by the client–server model.",
        "data migration": "The process of transferring data between storage types, formats, or computer systems.",
        "data replication": "The process of copying data from one location to another in order to ensure the availability, reliability, and fault tolerance of the data.",
        "data center": "A facility composed of networked computers and storage used to organize, process, store, and disseminate large amounts of data.",
        "data mining": "The process of discovering patterns in large data sets involving methods at the intersection of machine learning, statistics, and database systems.",
        "data lake": "A centralized repository that allows you to store all your structured and unstructured data at any scale.",
        "cloud-native": "A term used to describe applications built to run optimally in cloud environments.",
        "cloud migration": "The process of moving data, applications, and other business elements from an organization's on-premises infrastructure to the cloud or from one cloud service to another.",
        "serverless database": "A database service that allows developers to build and run applications without having to manage infrastructure.",
        "cloud-native database": "A database service that is designed to take advantage of the scalability, agility, and flexibility of cloud computing.",
        "data modeling": "The process of creating a data model for an information system by applying formal data modeling techniques.",
        "data visualization": "The graphical representation of information and data, intended to help users understand complex data sets through visual context.",
        "cloud security": "The practice of protecting cloud environments from security threats and vulnerabilities.",
        "multi-cloud": "A cloud strategy that involves using multiple cloud computing and storage services in a single architecture.",
        "cloud migration strategy": "A plan for moving digital assets, services, and applications to a cloud computing environment.",
        "MongoDB": "A popular open-source NoSQL database that uses a document-oriented data model to store data in flexible, JSON-like documents with dynamic schemas.",
        "document": "A record in a MongoDB collection, which is similar to a row in a relational database table.",
        "collection": "A group of MongoDB documents, equivalent to a table in a relational database.",
        "field": "A key-value pair in a MongoDB document, equivalent to a column in a relational database table.",
        "index": "An optional feature in MongoDB that improves the performance of queries by making it faster to retrieve data.",
        "aggregation pipeline": "A framework in MongoDB for data aggregation operations that process documents and return computed results.",
        "replica set": "A group of MongoDB servers that maintain the same data set, providing redundancy and high availability.",
        "sharding": "A method for distributing data across multiple machines to support deployments with very large data sets and high throughput operations.",
        "gridFS": "A specification for storing and retrieving large files in MongoDB, which divides a file into smaller chunks called GridFS chunks.",
        "MongoDB Atlas": "A fully managed cloud database service provided by MongoDB that offers automated provisioning and scaling of databases.",
        "MQL": "MongoDB Query Language - a query language used to interact with MongoDB databases.",
        "BSON": "Binary JSON - a binary serialization format used to store documents and make remote procedure calls in MongoDB.",
        "MongoDB Compass": "A graphical user interface (GUI) for MongoDB that allows users to explore and manipulate databases visually.",
        "MongoDB Realm": "A serverless application platform that allows developers to build modern, scalable applications with MongoDB as the backend database.",
        "MongoDB Stitch": "A serverless platform for MongoDB that provides easy access to MongoDB Atlas and other services for building modern applications.",
        "MongoDB Shell": "A command-line interface (CLI) for interacting with MongoDB databases, allowing users to run queries and commands.",
        "MongoDB Enterprise": "A commercial version of MongoDB that includes additional features and support for enterprise deployments.",
        "operating system": "Software that manages computer hardware and provides common services for computer programs. Examples include Windows, macOS, Linux, and Unix.",
        "kernel": "The core component of an operating system that provides low-level services such as process management, memory management, and device management.",
        "file system": "A method for storing and organizing computer files and the data they contain. It defines how data is stored, retrieved, and updated on a storage device.",
        "process": "An instance of a program running on a computer. It consists of the program code, current activity, and a set of system resources.",
        "thread": "A lightweight process that can run concurrently with other threads within the same process. Threads share the same memory space and resources.",
        "scheduler": "A component of the operating system responsible for allocating CPU time to processes and threads based on scheduling algorithms.",
        "interrupt": "A signal sent to the processor from an external device, indicating that it requires attention. Interrupts are used for hardware communication and handling asynchronous events.",
        "virtual memory": "A memory management technique that provides an abstraction of the computer's physical memory, allowing processes to use more memory than is physically available.",
        "paging": "A memory management scheme that allows the operating system to move data between RAM and disk storage to optimize memory usage.",
        "file descriptor": "An abstract indicator (usually a small integer) that represents an open file or other I/O resource in a computer program.",
        "system call": "An interface provided by the operating system that allows user-level processes to request services from the kernel, such as reading and writing files or creating new processes.",
        "device driver": "A software component that allows the operating system to communicate with hardware devices, enabling the use of peripherals such as printers, keyboards, and network adapters.",
        "shell": "A command-line interface (CLI) or graphical user interface (GUI) that allows users to interact with the operating system by entering commands or using menus and windows.",
        "booting": "The process of starting up a computer and loading the operating system into memory.",
        "authentication": "The process of verifying the identity of a user or system, usually through the use of usernames, passwords, and other authentication factors.",
        "authorization": "The process of determining whether a user or system has permission to access a particular resource or perform a specific action.",
        "file permission": "Settings that determine who can read, write, or execute a file on a computer system, usually specified for the owner, group, and other users.",
        "process control block": "A data structure in the operating system kernel that stores information about a process, including its state, program counter, and CPU registers.",
        "system resource": "Any physical or virtual component of a computer system that can be managed and allocated by the operating system, such as CPU time, memory, and disk space.",
        "multi-user": "An operating system feature that allows multiple users to interact with the system simultaneously, each with their own user account and resources.",
        "multi-tasking": "An operating system feature that allows multiple programs to run concurrently on a computer system, sharing the CPU's processing time.",
        "multi-processing": "An operating system feature that allows a computer system to use multiple CPUs or CPU cores to execute processes simultaneously, improving performance and scalability.",
        "file system hierarchy": "The organization of files and directories on a storage device, typically represented as a tree structure with a root directory at the top.",
        "system log": "A record of events and activities that occur within an operating system or software application, used for troubleshooting, auditing, and monitoring purposes.",
        "system clock": "A hardware component that generates regular, recurring signals used by the operating system to control timing and synchronization.",
        "system tray": "A notification area on the taskbar of a graphical user interface where icons for system and application notifications are displayed.",
        "task manager": "A system utility in operating systems that allows users to view and manage running processes, monitor system performance, and configure system settings.",
        "command interpreter": "A program that interprets and executes commands entered by users or other software, often referred to as a shell in Unix-like operating systems.",
        "system administrator": "A person responsible for managing and maintaining computer systems and networks, including installing, configuring, and troubleshooting hardware and software.",
        "network": "A group of interconnected devices or nodes that can communicate with each other to share resources and information.",
        "protocol": "A set of rules and conventions that govern how data is transmitted and received over a network.",
        "IP address": "A numerical label assigned to each device connected to a computer network that uses the Internet Protocol for communication.",
        "subnet mask": "A bitmask used to divide an IP address into network and host portions to determine the network prefix.",
        "router": "A networking device that forwards data packets between computer networks, facilitating communication between devices on different networks.",
        "switch": "A networking device that connects devices together on a local area network (LAN) and forwards data packets to their intended destination.",
        "hub": "A basic networking device that connects multiple devices in a LAN and broadcasts data packets to all connected devices.",
        "firewall": "A network security device that monitors and controls incoming and outgoing network traffic based on predetermined security rules.",
        "gateway": "A network node that serves as an entry point to another network, typically connecting different types of networks, such as a LAN to the Internet.",
        "DNS": "Domain Name System - a hierarchical and decentralized naming system for computers, services, or other resources connected to the Internet or a private network.",
        "DHCP": "Dynamic Host Configuration Protocol - a network management protocol used to automatically assign IP addresses and other network configuration parameters to devices.",
        "LAN": "Local Area Network - a network that connects computers and devices in a limited geographical area, such as a home, office, or campus.",
        "WAN": "Wide Area Network - a network that spans a large geographical area and connects multiple LANs or other networks together.",
        "VPN": "Virtual Private Network - a secure network connection that allows users to access resources and services over a public network, such as the Internet, as if they were directly connected to a private network.",
        "TCP": "Transmission Control Protocol - a connection-oriented protocol used for reliable and ordered delivery of data packets over a network.",
        "UDP": "User Datagram Protocol - a connectionless protocol used for sending datagrams over a network without the need for a connection.",
        "MAC address": "Media Access Control address - a unique identifier assigned to network interfaces for communications on a network segment.",
        "ARP": "Address Resolution Protocol - a protocol used to map IP addresses to MAC addresses on a local network.",
        "ICMP": "Internet Control Message Protocol - a network layer protocol used to send error messages and operational information indicating problems with packet delivery.",
        "NAT": "Network Address Translation - a process used to modify IP address information in packet headers while in transit across a router or firewall.",
        "subnet": "A logical subdivision of an IP network, typically used to divide a larger network into smaller, more manageable segments.",
        "bandwidth": "The maximum rate of data transfer across a network path, usually measured in bits per second (bps) or bytes per second (Bps).",
        "latency": "The time delay between the initiation of a network request and the receipt of a response, typically measured in milliseconds (ms).",
        "packet": "A unit of data transmitted over a network, consisting of a header containing control information and payload containing the actual data.",
        "routing": "The process of selecting the best path for data packets to travel from the source to the destination across a network.",
        "port": "A logical construct that represents an endpoint of communication in a network, identified by a numerical value.",
        "TCP/IP": "Transmission Control Protocol/Internet Protocol - the basic communication language or protocol of the Internet.",
        "subnetting": "The process of dividing a single large network into smaller, more manageable subnetworks to improve performance, security, and efficiency.",
        "network topology": "The arrangement of nodes and links in a network, defining how devices are connected and communicate with each other.",
        "DNS server": "A server that translates domain names into IP addresses and vice versa, enabling users to access websites and other resources using human-readable names.",
        "load balancing": "The process of distributing incoming network traffic across multiple servers to ensure no single server bears too much demand.",
        "port forwarding": "The process of redirecting network traffic from one network port to another, typically used to enable access to services hosted on internal servers from external networks.",
        "network security": "The protection of computer networks and their data from unauthorized access, misuse, or modification.",
        "packet sniffing": "The practice of intercepting and analyzing data packets as they pass through a network interface, typically for the purpose of monitoring or capturing network traffic.",
        "man-in-the-middle attack": "A cyberattack where an attacker intercepts and potentially alters communications between two parties without their knowledge or consent.",
        "intrusion detection system (IDS)": "A security software or device that monitors network or system activities for malicious activities or policy violations.",
        "intrusion prevention system (IPS)": "A security software or device that actively monitors and blocks potentially malicious traffic or activities on a network or system.",
        "denial-of-service (DoS) attack": "A cyberattack where an attacker floods a network, server, or service with excessive requests to disrupt normal traffic or functionality.",
        "distributed denial-of-service (DDoS) attack": "A type of DoS attack where multiple compromised systems are used to launch a coordinated attack against a single target, increasing the scale and impact of the attack.",
        "port scanning": "The process of probing a network for open ports on target systems to identify potential vulnerabilities or services running on those ports.",
        "subnet mask": "A bitmask used to divide an IP address into network and host portions to determine the network prefix.",
        "VLAN": "Virtual Local Area Network - a logical group of devices within the same physical network that communicate as if they were on separate physical networks.",
        "MAC table": "A table maintained by a switch that maps MAC addresses to switch ports, used to forward data frames to the correct destination.",
        "data structure": "A way of organizing and storing data in a computer's memory for efficient access and manipulation.",
        "array": "A data structure consisting of a collection of elements, each identified by an index or key.",
        "linked list": "A linear data structure consisting of a sequence of elements, where each element points to the next element in the sequence.",
        "stack": "A linear data structure that follows the Last In, First Out (LIFO) principle, where elements are added and removed from the same end, called the top.",
        "queue": "A linear data structure that follows the First In, First Out (FIFO) principle, where elements are added at the rear and removed from the front.",
        "tree": "A hierarchical data structure consisting of nodes connected by edges, with a single root node at the top and branches extending downwards.",
        "binary tree": "A tree data structure in which each node has at most two children, referred to as the left child and the right child.",
        "binary search tree": "A binary tree data structure in which the value of each node's left child is less than the node's value, and the value of each node's right child is greater than the node's value.",
        "heap": "A binary tree-based data structure that satisfies the heap property, where the value of each parent node is greater than or equal to the values of its children.",
        "graph": "A non-linear data structure consisting of a collection of nodes (vertices) and edges that connect pairs of nodes.",
        "hash table": "A data structure that implements an associative array abstract data type, allowing rapid insertion, deletion, and lookup of key-value pairs.",
        "trie": "A tree data structure used for storing a dynamic set of strings, where each node represents a common prefix of its descendants.",
        "dynamic array": "A resizable array data structure that grows or shrinks in size as needed to accommodate elements.",
        "hash map": "An implementation of a hash table data structure that uses a hash function to map keys to indices in an array.",
        "priority queue": "An abstract data type that operates similar to a regular queue but where each element has an associated priority value.",
        "bloom filter": "A space-efficient probabilistic data structure used to test whether an element is a member of a set.",
        "segment tree": "A tree data structure used for storing intervals or segments, allowing efficient querying and updating of segment-related information.",
        "suffix array": "A sorted array of all suffixes of a given string, used in various string processing algorithms.",
        "trie": "A tree data structure used to store a dynamic set of strings, where each node represents a common prefix of its descendants.",
        "red-black tree": "A self-balancing binary search tree data structure that ensures logarithmic time complexity for insertion, deletion, and search operations.",
        "AVL tree": "A self-balancing binary search tree data structure that maintains a balanced condition based on the height difference of subtrees.",
        "B-tree": "A self-balancing tree data structure designed to work well with secondary storage devices and large datasets.",
        "graph traversal": "The process of visiting and exploring all the nodes in a graph in a systematic manner.",
        "breadth-first search (BFS)": "A graph traversal algorithm that explores the neighbor nodes at the present depth prior to moving on to the nodes at the next depth level.",
        "depth-first search (DFS)": "A graph traversal algorithm that explores as far as possible along each branch before backtracking.",
        "Dijkstra's algorithm": "An algorithm for finding the shortest paths between nodes in a graph, which may represent, for example, road networks.",
        "Bellman-Ford algorithm": "An algorithm for finding the shortest paths from a single source node to all other nodes in a weighted graph.",
        "Floyd-Warshall algorithm": "An algorithm for finding the shortest paths between all pairs of nodes in a weighted graph.",
        "dynamic programming": "A method for solving complex problems by breaking them down into simpler subproblems and solving each subproblem only once, storing the solutions to subproblems in a table.",
        "greedy algorithm": "An algorithmic paradigm that follows the problem-solving heuristic of making the locally optimal choice at each stage with the hope of finding a global optimum.",
        "divide and conquer": "An algorithmic paradigm that breaks a problem into smaller subproblems, solves the subproblems recursively, and then combines their solutions to solve the original problem.",
        "backtracking": "A problem-solving technique that explores all possible solutions to a computational problem by constructing a solution incrementally and abandoning it if it's determined that the solution cannot be completed.",
        "binary search": "A search algorithm that finds the position of a target value within a sorted array by repeatedly dividing the search interval in half.",
        "hashing": "A technique that maps data of arbitrary size to fixed-size values, typically for indexing and retrieval purposes in data structures such as hash tables.",
        "sorting algorithm": "An algorithm that arranges elements of a list or array in a specific order, such as numerical or lexicographical order.",
        "merge sort": "A sorting algorithm that divides the input array into two halves, recursively sorts each half, and then merges the sorted halves.",
        "quick sort": "A sorting algorithm that divides the input array into two partitions, selects a pivot element, partitions the array into elements smaller than the pivot and elements greater than the pivot, and then recursively sorts the partitions.",
        "bubble sort": "A simple sorting algorithm that repeatedly steps through the list, compares adjacent elements, and swaps them if they are in the wrong order.",
        "insertion sort": "A simple sorting algorithm that builds the final sorted array one element at a time by inserting each element into its correct position.",
        "selection sort": "A simple sorting algorithm that repeatedly selects the smallest (or largest) element from the unsorted portion of the array and moves it to its correct position in the sorted portion.",
        "MongoDB": "A popular open-source NoSQL database that uses a document-oriented data model to store data in flexible, JSON-like documents with dynamic schemas.",
        "radix sort": "A non-comparative sorting algorithm that sorts data with integer keys by grouping keys by individual digits that share the same significant position and value.",
        # Add more data structure and algorithm-related terms and their definitions as needed
    }
    
    # Check if the word is a technical term and return its definition
    return technical_dictionary.get(word.lower())

# Main application logic
def main_app():
    st.set_page_config(layout="wide")

    choice = st.sidebar.selectbox("Select your choice", ["Summarize Text", "Summarize Document", "Retrieve Content", "Simple Dictionary", "Sentiment Analysis"])

    if choice == "Summarize Text":
        st.subheader("Summarize Text using NLTK")
        input_text = st.text_area("Enter your text here")
        if input_text is not None:
            if st.button("Summarize Text"):
                summary = summarize_text(input_text)
                st.subheader("Input Text")
                st.info(input_text)
                st.subheader("Summarized Text")
                st.success(summary)

    elif choice == "Summarize Document":
        st.subheader("Summarize Document using NLTK")
        input_file = st.file_uploader("Upload your document", type=["pdf"])
        if input_file is not None:
            if st.button("Summarize Document"):
                with open("doc_file.pdf", "wb") as f:
                    f.write(input_file.getbuffer())
                extracted_text = extract_text_from_pdf("doc_file.pdf")
                summary = summarize_text(extracted_text)
                st.subheader("Extracted Text from Document")
                st.info(extracted_text)
                st.subheader("Summarized Text")
                st.success(summary)

    elif choice == "Retrieve Content":
        st.subheader("Retrieve Content from Wikipedia")
        topic = st.text_input("Enter a topic to retrieve content from Wikipedia")

        if st.button("Retrieve Content"):
            if topic:
                retrieved_content = retrieve_content(topic)
                if retrieved_content:
                    st.success("Content Retrieved Successfully:")
                    for paragraph in retrieved_content:
                        st.write(paragraph)
                else:
                    st.error("Failed to retrieve content. Please try again with a different topic.")
            else:
                st.warning("Please enter a topic to retrieve content.")

    elif choice == "Simple Dictionary":
        st.subheader("Simple Dictionary")

        word = st.text_input("Enter a word")
        if st.button("Define"):
            if word:
                # Check if the word is a technical term
                technical_definition = get_technical_definitions(word)
                if technical_definition:
                    st.success("Technical Definition:")
                    st.write(technical_definition)
                else:
                    # If not a technical term, retrieve definitions from WordNet
                    definitions = get_word_definitions(word)
                    if definitions:
                        st.success("Definitions:")
                        for definition in definitions:
                            st.write(definition)
                    else:
                        st.error("No definitions found for the given word.")
            else:
                st.warning("Please enter a word.")
    
    elif choice == "Sentiment Analysis":
        st.title("Sentiment Analysis")

        text_to_analyze = st.text_area("Enter the text to analyze")
        
        if st.button("Analyze Sentiment"):
            if text_to_analyze:
                # Perform sentiment analysis
                sentiment_scores = sia.polarity_scores(text_to_analyze)

                # Interpret sentiment scores
                compound_score = sentiment_scores['compound']
                if compound_score >= 0.05:
                    sentiment_label = "Positive"
                elif compound_score <= -0.05:
                    sentiment_label = "Negative"
                else:
                    sentiment_label = "Neutral"

                # Display result
                st.success(f"Sentiment Analysis Result: {sentiment_label} (Compound Score: {compound_score})")
            else:
                st.warning("Please enter the text to analyze.")

# Function for login page
def login_page():
    col1,col2,col3 = st.columns([1,2,1])

    # Authentication form layout
    do_you_have_an_account = col2.selectbox(label='Do you have an account?',options=('Yes','No','I forgot my password'))
    auth_form = col2.form(key='Authentication form',clear_on_submit=False)
    email = auth_form.text_input(label='Email')
    password = auth_form.text_input(label='Password',type='password') if do_you_have_an_account in {'Yes','No'} else auth_form.empty()
    auth_notification = col2.empty()

    # Sign In
    if do_you_have_an_account == 'Yes' and auth_form.form_submit_button(label='Sign In',use_container_width=True,type='primary'):
        with auth_notification, st.spinner('Signing in'):
            auth_functions.sign_in(email,password)

    # Create Account
    elif do_you_have_an_account == 'No' and auth_form.form_submit_button(label='Create Account',use_container_width=True,type='primary'):
        with auth_notification, st.spinner('Creating account'):
            auth_functions.create_account(email,password)

    # Password Reset
    elif do_you_have_an_account == 'I forgot my password' and auth_form.form_submit_button(label='Send Password Reset Email',use_container_width=True,type='primary'):
        with auth_notification, st.spinner('Sending password reset link'):
            auth_functions.reset_password(email)

    # Authentication success and warning messages
    if 'auth_success' in st.session_state:
        auth_notification.success(st.session_state.auth_success)
        del st.session_state.auth_success
    elif 'auth_warning' in st.session_state:
        auth_notification.warning(st.session_state.auth_warning)
        del st.session_state.auth_warning

# Main Streamlit app
def main():
    if 'user_info' not in st.session_state:
        login_page()
    else:

        # text summarizer page
        main_app()

        # Sign out
        st.header('Sign out:')
        st.button(label='Sign Out',on_click=auth_functions.sign_out,type='primary')

        # Delete Account
        st.header('Delete account:')
        password = st.text_input(label='Confirm your password',type='password')
        st.button(label='Delete Account',on_click=auth_functions.delete_account,args=[password],type='primary')

if __name__ == "__main__":
    main()
