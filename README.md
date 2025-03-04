
# **vLEI Verifier Router**

The **vLEI Verifier Router** is a service that routes requests to multiple instances of the [vLEI Verifier](https://github.com/GLEIF-IT/vlei-verifier). It manages the distribution of requests across verifier instances and ensures efficient load balancing and failover handling.

----------

## **Features**


-   **Request Routing**: Routes requests to appropriate vLEI Verifier instances based on AID or SAID.
    
-   **Load Balancing**: Distributes requests evenly across multiple verifier instances.
    
-   **Failover Handling**: Automatically reroutes requests if a verifier instance becomes unavailable.
    
-   **Redis Integration**: Stores all **AID-to-verifier mappings** in Redis for persistence and scalability.
    
-   **Health Checks**: Monitors the health of verifier instances and routes traffic only to healthy instances.

    

----------

## **Getting Started**
    

### **Installation**

1.  Clone the repository:
	```bash
	    git clone https://github.com/GLEIF-IT/vlei-verifier-router.git
	    cd vlei-verifier-router	
	```
    
2.  Install dependencies:
    
    ```bash
	    pip install -r requirements.txt	
	 ```  
    

### **Running the Service**

#### **Locally**

1.  Start the service locally:
    
    ```bash
	    python -m uvicorn main:app --reload --port 7676
	 ```     
        
2.  Access the service at:
    
    ```bash
	    http://localhost:8000
	 ```
    
#### **Using Docker Compose**

The repository includes two `docker-compose` files for different use cases:

1.  **`docker-compose.yml`**:
    
    -   This file is for a **clean run** with no pre-configured `vlei-verifier` instances.
        
    -   After starting the router, you need to add `vlei-verifier` instances one by one using the **POST `/add_verifier_instance`** endpoint.
        
    -   To start the services:
        
        bash
       ```                
        docker-compose up -d
     ```
        
2.  **`docker-compose-test.yml`**:
    
    -   This file is for **testing** and includes **3 pre-configured `vlei-verifier` instances**.
        
    -   It also includes additional services like `vlei-server` and `witness-demo` for a complete testing environment.
        
    -   To start the services:
        
       ``` bash        
        docker-compose -f docker-compose-test.yml up -d
      ```
    

## **API Endpoints**

-   **POST `/presentation`**: Handle presentation requests for a given SAID and vLEI.
    
-   **GET `/authorization`**: Handle authorization requests for a given AID.
    
-   **POST `/signed-headers-verification`**: Verify signed headers for a given AID, signature, and serialized data.
    
-   **POST `/signature-verification`**: Verify signatures for a given AID, signature, and digest.
    
-   **POST `/add-root-of-trust`**: Add a root of trust to all verifier instances for a given AID, vLEI, and OOBI.
