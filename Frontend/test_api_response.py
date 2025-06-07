import requests
import json

print("Testing patient API response format")
print("==================================")

try:
    # Start the Flask server in a separate terminal window first
    # Make sure Flask is running on http://localhost:5000
    
    # Try to fetch patient with ID 110
    response = requests.get('http://localhost:5000/patients/api/110')
    
    # Print status code
    print(f"Status code: {response.status_code}")
    
    # Check if successful
    if response.status_code == 200:
        # Get the data
        data = response.json()
        
        # Print the full JSON response
        print("\nFull JSON response:")
        print(json.dumps(data, indent=2))
        
        # Check if all required fields are present
        required_fields = [
            "Patient_ID", 
            "Name", 
            "Age", 
            "Gender", 
            "Blood_Group", 
            "Contact_Number", 
            "Medical_History"
        ]
        
        # Check and print each field
        print("\nRequired fields check:")
        for field in required_fields:
            if field in data:
                print(f"✓ {field}: {data[field]}")
            else:
                print(f"✗ {field}: MISSING")
                
        # Overall result
        if all(field in data for field in required_fields):
            print("\nSUCCESS: All required fields are present in the API response")
        else:
            print("\nFAILURE: Some required fields are missing from the API response")
    else:
        print(f"Error: Received status code {response.status_code}")
        try:
            error_data = response.json()
            print(f"Error details: {error_data}")
        except:
            print(f"Raw response: {response.text}")
            
except Exception as e:
    print(f"Error testing API: {str(e)}")
    print("Make sure Flask server is running with 'python app.py'") 