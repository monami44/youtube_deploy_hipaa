'use client';

import { useState, useRef } from 'react';
import { uploadDocument } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';

export function UploadForm() {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const resetForm = () => {
    setFile(null);
    setError(null);
    setSuccess(false);
    setDocumentId(null);
    setUploadProgress(0);
    // Reset the file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    // Check if file is a PDF
    if (file.type !== 'application/pdf') {
      setError('Please upload a PDF file');
      return;
    }

    // Check file size (limit to 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size should be less than 10MB');
      return;
    }

    setIsUploading(true);
    setError(null);
    
    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 95) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 5;
        });
      }, 200);
      
      // Upload the document
      const result = await uploadDocument(file);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      setSuccess(true);
      setDocumentId(result.id);
      
      // Reset form after 3 seconds on success
      setTimeout(() => {
        resetForm();
      }, 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload document');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Card className="p-6 w-full max-w-md">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="file" className="block text-sm font-medium mb-2">
            Upload Document (PDF)
          </label>
          <Input
            ref={fileInputRef}
            id="file"
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
            disabled={isUploading}
            className="cursor-pointer"
          />
          {file && (
            <p className="mt-2 text-sm text-gray-500">
              Selected file: {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
            </p>
          )}
        </div>

        {isUploading && (
          <div className="space-y-2">
            <Progress value={uploadProgress} className="w-full h-2" />
            <p className="text-sm text-center">{uploadProgress}% uploaded</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 text-red-500 p-3 rounded-md text-sm">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-50 text-green-500 p-3 rounded-md text-sm">
            Document uploaded successfully! Document ID: {documentId}
          </div>
        )}

        <div className="flex justify-end">
          {!isUploading && (
            <Button type="button" variant="outline" className="mr-2" onClick={resetForm}>
              Reset
            </Button>
          )}
          <Button type="submit" disabled={isUploading || !file}>
            {isUploading ? 'Uploading...' : 'Upload'}
          </Button>
        </div>
      </form>
    </Card>
  );
} 