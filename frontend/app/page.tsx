import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import Link from "next/link";
import { PlusCircle } from "lucide-react";
import { getDocuments, Document } from "@/lib/api";
import { formatDistanceToNow } from "date-fns";

// Force dynamic rendering and disable caching
export const dynamic = 'force-dynamic';
export const revalidate = 0;

// This function fetches documents on the server
async function fetchDocuments() {
  console.log('Server-side: Fetching documents');
  try {
    const data = await getDocuments();
    console.log(`Server-side: Successfully fetched ${data.length} documents`);
    return { documents: data, error: null };
  } catch (error) {
    console.error('Server-side: Error fetching documents:', error);
    return { 
      documents: [], 
      error: error instanceof Error ? error.message : 'Failed to fetch documents' 
    };
  }
}

export default async function Home() {
  // Call the fetch function
  const { documents, error } = await fetchDocuments();
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Document Processor</h1>
        <Link href="/upload">
          <Button>
            <PlusCircle className="mr-2 h-4 w-4" />
            Upload Document
          </Button>
        </Link>
      </div>
      
      {error && (
        <div className="p-4 border border-red-500 bg-red-50 text-red-700 rounded-md">
          Error loading documents: {error}
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Real documents from the backend */}
        {documents.map((doc) => (
        <DocumentCard
            key={doc.id}
            title={doc.filename || "Unnamed Document"}
            description={doc.uploadDate ? `Uploaded ${formatDistanceToNow(new Date(doc.uploadDate))} ago` : "Upload date unknown"}
            status={formatStatus(doc.status)}
            id={doc.id}
          />
        ))}
        
        {/* Add new document card */}
        <Link href="/upload" className="h-full">
          <Card className="h-full border-dashed flex items-center justify-center hover:border-primary/50 transition-colors cursor-pointer">
            <CardContent className="flex flex-col items-center justify-center p-6">
              <PlusCircle className="h-12 w-12 text-muted-foreground" />
              <p className="mt-2 text-sm text-muted-foreground">Upload New Document</p>
            </CardContent>
          </Card>
        </Link>
      </div>
      
      {documents.length === 0 && !error && (
        <div className="text-center py-10">
          <p className="text-muted-foreground">No documents found. Upload a document to get started.</p>
        </div>
      )}
    </div>
  );
}

function formatStatus(status: string): string {
  // Capitalize first letter
  return status.charAt(0).toUpperCase() + status.slice(1);
}

function DocumentCard({ title, description, status, id }: { 
  title: string; 
  description: string; 
  status: string;
  id: string;
}) {
  // Determine status color
  const statusColor = 
    status.toLowerCase() === "completed" ? "bg-green-500" :
    status.toLowerCase() === "processing" ? "bg-yellow-500" :
    status.toLowerCase() === "pending" ? "bg-blue-500" : 
    status.toLowerCase() === "error" ? "bg-red-500" : "bg-gray-500";

  return (
    <Link href={`/documents/${id}`}>
      <Card className="h-full hover:border-primary/50 transition-colors cursor-pointer">
        <CardHeader>
          <CardTitle className="truncate">{title}</CardTitle>
          <CardDescription>{description}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center">
            <div className={`h-2 w-2 rounded-full mr-2 ${statusColor}`} />
            <span className="text-sm text-muted-foreground">{status}</span>
          </div>
        </CardContent>
        <CardFooter>
          <p className="text-sm text-muted-foreground">Click to view details</p>
        </CardFooter>
      </Card>
    </Link>
  );
}
