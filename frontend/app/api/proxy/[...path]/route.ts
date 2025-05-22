import { NextRequest, NextResponse } from 'next/server';

// Get the API URL from environment variable
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/');
  const apiUrl = `${API_URL}/api/${path}`;
  
  console.log(`Proxying GET request to: ${apiUrl}`);
  
  try {
    const response = await fetch(apiUrl);
    const data = await response.json();
    
    return NextResponse.json(data);
  } catch (error) {
    console.error(`Error proxying GET request to ${apiUrl}:`, error);
    return NextResponse.json(
      { error: 'Failed to fetch data from backend' }, 
      { status: 500 }
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/');
  const apiUrl = `${API_URL}/api/${path}`;
  
  // Get the request body
  const body = await request.json();
  
  console.log(`Proxying POST request to: ${apiUrl}`, body);
  
  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error(`Error proxying POST request to ${apiUrl}:`, error);
    return NextResponse.json(
      { error: 'Failed to post data to backend' }, 
      { status: 500 }
    );
  }
} 