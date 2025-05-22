import { notFound } from "next/navigation";
import { getDocument, Document } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { RegenerateSummaryButton } from "@/components/regenerate-summary-button";

// Ensure page is server-side rendered and dynamic
export const dynamic = 'force-dynamic';
export const revalidate = 0;

export default async function DocumentPage({ params }: { params: { id: string } }) {
  let document: Document | null = null;
  try {
    document = await getDocument(params.id);
  } catch (error) {
    // If document not found or error fetching
    notFound();
  }

  if (!document) {
    notFound();
  }

  // Function to format the status display
  const getStatusDisplay = (status: string) => {
    const statusColor = 
      status === "completed" ? "bg-green-500" :
      status === "processing" ? "bg-yellow-500" :
      status === "pending" ? "bg-blue-500" : 
      status === "error" ? "bg-red-500" : "bg-gray-500";
    
    const statusText = status.charAt(0).toUpperCase() + status.slice(1);
    
    return (
      <div className="flex items-center">
        <div className={`h-3 w-3 rounded-full mr-2 ${statusColor}`} />
        <span>{statusText}</span>
      </div>
    );
  };

  // Format dates for display
  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString();
    } catch (e) {
      return "Unknown date";
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Link href="/">
            <Button variant="outline" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <h1 className="text-2xl font-bold">{document.filename}</h1>
        </div>
        <div className="flex items-center">
          {getStatusDisplay(document.status)}
        </div>
      </div>

      {/* Document information */}
      <Card>
        <CardHeader>
          <CardTitle>Document Information</CardTitle>
          <CardDescription>Details about this document</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">ID</p>
              <p className="text-sm font-medium">{document.id}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Uploaded</p>
              <p className="text-sm font-medium">{formatDate(document.uploadDate)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Filename</p>
              <p className="text-sm font-medium">{document.filename}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Status</p>
              <p className="text-sm font-medium">{document.status}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Document Summary</CardTitle>
          <CardDescription>AI-generated summary of the document contents</CardDescription>
        </CardHeader>
        <CardContent>
          {document.summary ? (
            <div className="whitespace-pre-wrap">{document.summary}</div>
          ) : (
            <div className="text-muted-foreground italic">
              {document.status === "completed" ? 
                "No summary is available for this document." : 
                "Summary will be available once document processing is complete."}
            </div>
          )}
        </CardContent>
        {document.status === "completed" && (
          <CardFooter>
            <RegenerateSummaryButton documentId={document.id} />
          </CardFooter>
        )}
      </Card>
    </div>
  );
} 