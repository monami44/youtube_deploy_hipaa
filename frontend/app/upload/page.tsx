import { UploadForm } from '@/components/upload-form';

export default function UploadPage() {
  return (
    <div className="container mx-auto py-8 space-y-6">
      <h1 className="text-2xl font-bold">Upload Document</h1>
      <p className="text-gray-600">Upload PDF documents to be processed by our system. The documents will be analyzed and a summary will be generated.</p>
      
      <div className="mt-8 flex justify-center">
        <UploadForm />
      </div>
    </div>
  );
} 