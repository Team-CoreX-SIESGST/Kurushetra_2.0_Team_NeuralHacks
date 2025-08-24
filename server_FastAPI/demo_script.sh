#!/bin/bash

# OmniSearch AI Demo Script
# This script demonstrates the basic functionality of the OmniSearch AI API

echo "🚀 Starting OmniSearch AI Demo"
echo "================================"

# Configuration
API_BASE="http://localhost:8000"
WORKSPACE_ID="demo-workspace"
TOKEN="your_auth_token_here"  # Replace with actual token

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if API is running
check_api() {
    print_status "Checking if API is running..."
    if curl -s "$API_BASE/health" > /dev/null; then
        print_status "API is running at $API_BASE"
    else
        print_error "API is not running. Please start the server first:"
        echo "  uvicorn app.main:app --reload --port 8000"
        exit 1
    fi
}

# Test health endpoint
test_health() {
    print_status "Testing health endpoint..."
    response=$(curl -s "$API_BASE/health")
    echo "Health check response: $response"
}

# Test root endpoint
test_root() {
    print_status "Testing root endpoint..."
    response=$(curl -s "$API_BASE/")
    echo "Root endpoint response: $response"
}

# Test file upload (if sample file exists)
test_upload() {
    if [ -f "sample_data/sample.pdf" ]; then
        print_status "Testing file upload..."
        response=$(curl -s -X POST "$API_BASE/api/v1/upload" \
            -H "Authorization: Bearer $TOKEN" \
            -F "workspace_id=$WORKSPACE_ID" \
            -F "file=@sample_data/sample.pdf")
        echo "Upload response: $response"
        
        # Extract file_id from response for later use
        FILE_ID=$(echo $response | grep -o '"file_id":"[^"]*"' | cut -d'"' -f4)
        if [ ! -z "$FILE_ID" ]; then
            echo "FILE_ID=$FILE_ID" > .demo_file_id
            print_status "File uploaded with ID: $FILE_ID"
        fi
    else
        print_warning "Sample PDF not found. Skipping upload test."
        print_warning "Create sample_data/sample.pdf to test upload functionality."
    fi
}

# Test search functionality
test_search() {
    print_status "Testing search functionality..."
    
    # Test simple search
    print_status "Testing simple search..."
    response=$(curl -s -X GET "$API_BASE/api/v1/search/simple?workspace_id=$WORKSPACE_ID&query=test&top_k=5" \
        -H "Authorization: Bearer $TOKEN")
    echo "Simple search response: $response"
    
    # Test full search pipeline
    print_status "Testing full search pipeline..."
    response=$(curl -s -X POST "$API_BASE/api/v1/search" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"workspace_id\": \"$WORKSPACE_ID\",
            \"query\": \"Summarize the main points\",
            \"top_k\": 10,
            \"include_web\": true,
            \"rerank\": true,
            \"summarize\": true
        }")
    echo "Full search response: $response"
}

# Test file operations (if file was uploaded)
test_file_operations() {
    if [ -f ".demo_file_id" ]; then
        source .demo_file_id
        print_status "Testing file operations for file: $FILE_ID"
        
        # Test file info
        print_status "Getting file information..."
        response=$(curl -s -X GET "$API_BASE/api/v1/file/$FILE_ID?workspace_id=$WORKSPACE_ID" \
            -H "Authorization: Bearer $TOKEN")
        echo "File info response: $response"
        
        # Test file metadata
        print_status "Getting file metadata..."
        response=$(curl -s -X GET "$API_BASE/api/v1/file/$FILE_ID/metadata?workspace_id=$WORKSPACE_ID" \
            -H "Authorization: Bearer $TOKEN")
        echo "File metadata response: $response"
        
        # Test file chunks
        print_status "Getting file chunks..."
        response=$(curl -s -X GET "$API_BASE/api/v1/file/$FILE_ID/chunks?workspace_id=$WORKSPACE_ID&limit=10" \
            -H "Authorization: Bearer $TOKEN")
        echo "File chunks response: $response"
        
        # Test file page (assuming page 1 exists)
        print_status "Getting file page 1..."
        response=$(curl -s -X GET "$API_BASE/api/v1/file/$FILE_ID/page/1?workspace_id=$WORKSPACE_ID" \
            -H "Authorization: Bearer $TOKEN")
        echo "File page response: $response"
        
        # Clean up
        rm -f .demo_file_id
    else
        print_warning "No file uploaded. Skipping file operation tests."
    fi
}

# Test workspace operations
test_workspace_operations() {
    print_status "Testing workspace operations..."
    
    # List files in workspace
    print_status "Listing files in workspace..."
    response=$(curl -s -X GET "$API_BASE/api/v1/files/$WORKSPACE_ID" \
        -H "Authorization: Bearer $TOKEN")
    echo "Workspace files response: $response"
    
    # Get search stats
    print_status "Getting search statistics..."
    response=$(curl -s -X GET "$API_BASE/api/v1/search/stats/$WORKSPACE_ID" \
        -H "Authorization: Bearer $TOKEN")
    echo "Search stats response: $response"
}

# Main execution
main() {
    echo ""
    print_status "Starting API tests..."
    echo ""
    
    check_api
    test_health
    test_root
    echo ""
    
    print_status "Testing core functionality..."
    echo ""
    test_upload
    test_search
    echo ""
    
    print_status "Testing file operations..."
    echo ""
    test_file_operations
    echo ""
    
    print_status "Testing workspace operations..."
    echo ""
    test_workspace_operations
    echo ""
    
    print_status "Demo completed!"
    echo ""
    print_status "Next steps:"
    echo "  1. Check the API documentation at $API_BASE/docs"
    echo "  2. Explore the interactive API playground"
    echo "  3. Review the logs for detailed information"
    echo "  4. Customize the demo script for your needs"
}

# Check if help is requested
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "OmniSearch AI Demo Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -t, --token    Set authentication token"
    echo "  -w, --workspace Set workspace ID"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Run with default settings"
    echo "  $0 -t my_token                       # Run with custom token"
    echo "  $0 -w my-workspace -t my_token      # Run with custom workspace and token"
    echo ""
    echo "Environment:"
    echo "  Make sure the FastAPI server is running on port 8000"
    echo "  Ensure you have a valid authentication token"
    echo "  Create sample_data/sample.pdf for upload testing"
    exit 0
fi

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--token)
            TOKEN="$2"
            shift 2
            ;;
        -w|--workspace)
            WORKSPACE_ID="$2"
            shift 2
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Validate token
if [ "$TOKEN" = "your_auth_token_here" ]; then
    print_error "Please set a valid authentication token:"
    echo "  $0 -t your_actual_token"
    echo "  or edit the script and set TOKEN variable"
    exit 1
fi

# Run the demo
main
