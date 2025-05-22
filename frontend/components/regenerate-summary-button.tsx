'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { RefreshCw } from 'lucide-react';
import { regenerateSummary } from '@/lib/api';
import { useRouter } from 'next/navigation';

interface RegenerateSummaryButtonProps {
  documentId: string;
}

export function RegenerateSummaryButton({ documentId }: RegenerateSummaryButtonProps) {
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleRegenerate = async () => {
    setIsRegenerating(true);
    setError(null);
    
    try {
      // Call the API to regenerate the summary
      // Using an empty prompt to use the default system prompt
      await regenerateSummary(documentId, '');
      
      // Refresh the page to show the new summary
      router.refresh();
    } catch (err) {
      console.error('Error regenerating summary:', err);
      setError(err instanceof Error ? err.message : 'Failed to regenerate summary');
    } finally {
      setIsRegenerating(false);
    }
  };

  return (
    <div className="space-y-2">
      <Button 
        onClick={handleRegenerate} 
        disabled={isRegenerating}
        variant="outline"
        className="w-full"
      >
        {isRegenerating ? (
          <>
            <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
            Regenerating...
          </>
        ) : (
          <>
            <RefreshCw className="mr-2 h-4 w-4" />
            Regenerate Summary
          </>
        )}
      </Button>
      
      {error && (
        <div className="text-sm text-red-500">
          {error}
        </div>
      )}
    </div>
  );
} 