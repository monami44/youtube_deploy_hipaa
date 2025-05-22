#!/bin/bash

# Azure PostgreSQL Setup Script for Document Processing Service
# This script creates the necessary database, tables, and indexes for the application

# Usage: setup_database.sh <server_name> <admin_username> <admin_password>

# Check if required arguments are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <server_name> <admin_username> <admin_password>"
    exit 1
fi

SERVER_NAME=$1
ADMIN_USERNAME=$2
ADMIN_PASSWORD=$3
DATABASE_NAME="docprocessor"

# Connect to the Azure PostgreSQL server and create database
echo "Creating database $DATABASE_NAME on $SERVER_NAME..."
PGPASSWORD=$ADMIN_PASSWORD psql -h $SERVER_NAME -U $ADMIN_USERNAME -d postgres -c "CREATE DATABASE $DATABASE_NAME;"

if [ $? -ne 0 ]; then
    echo "Failed to create database. Exiting."
    exit 1
fi

# Connect to the newly created database and create tables
echo "Creating tables in $DATABASE_NAME..."
PGPASSWORD=$ADMIN_PASSWORD psql -h $SERVER_NAME -U $ADMIN_USERNAME -d $DATABASE_NAME << EOF
-- Create UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    blob_url TEXT NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    extracted_text TEXT,
    summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);
CREATE INDEX IF NOT EXISTS idx_documents_filename ON documents(filename);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS \$\$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
\$\$ LANGUAGE plpgsql;

-- Create trigger for updated_at
DROP TRIGGER IF EXISTS set_timestamp ON documents;
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON documents
FOR EACH ROW
EXECUTE FUNCTION update_modified_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $ADMIN_USERNAME;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO $ADMIN_USERNAME;
EOF

if [ $? -ne 0 ]; then
    echo "Failed to create tables. Exiting."
    exit 1
fi

echo "Database setup completed successfully."
exit 0 