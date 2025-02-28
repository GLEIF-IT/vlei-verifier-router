
# **vLEI Verifier Router**

The **vLEI Verifier Router** is a service that routes requests to multiple instances of the [vLEI Verifier](https://github.com/GLEIF-IT/vlei-verifier). It manages the distribution of requests across verifier instances and ensures efficient load balancing and failover handling.

----------

## **Features**

-   **Request Routing**: Routes requests to appropriate vLEI Verifier instances based on AID or SAID. Before running the vlei-verifier-router update vlei_verifier_router_config.json configuration file with a valid list of verifier_instances.
    
-   **Load Balancing**: Distributes requests evenly across multiple verifier instances.
    
-   **Failover Handling**: Automatically reroutes requests if a verifier instance becomes unavailable.

    

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

1.  Start the service locally:
    
    ```bash
	    python -m uvicorn main:app --reload --port 7676
	 ```     
        
2.  Access the service at:
    
    ```bash
	    http://localhost:8000
	 ```  
    
    

## **API Endpoints**

-   **POST `/presentation`**: Handle presentation requests for a given SAID and vLEI.
    
-   **GET `/authorization`**: Handle authorization requests for a given AID.
    
-   **POST `/signed-headers-verification`**: Verify signed headers for a given AID, signature, and serialized data.
    
-   **POST `/signature-verification`**: Verify signatures for a given AID, signature, and digest.
    
-   **POST `/add-root-of-trust`**: Add a root of trust to all verifier instances for a given AID, vLEI, and OOBI.
